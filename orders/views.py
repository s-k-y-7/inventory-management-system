from rest_framework import views, status, generics
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db.models.functions import Coalesce
from stores.models import Store, Inventory
from products.models import Product
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderListSerializer

class OrderCreateAPIView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        store_id = serializer.validated_data['store_id']
        items = serializer.validated_data['items']

        store = get_object_or_404(Store, id=store_id)
        product_ids = [item['product_id'] for item in items]
        
        with transaction.atomic():
            # Lock the inventory rows for these products in this store to prevent race conditions
            inventories = Inventory.objects.select_for_update().filter(
                store=store, 
                product_id__in=product_ids
            )
            inventory_map = {inv.product_id: inv for inv in inventories}
            
            insufficient_stock = False
            
            # Create order as PENDING initially
            order = Order.objects.create(store=store, status=Order.StatusChoices.PENDING)
            
            order_items_to_create = []
            for item in items:
                prod_id = item['product_id']
                qty = item['quantity_requested']
                
                if prod_id not in inventory_map or inventory_map[prod_id].quantity < qty:
                    insufficient_stock = True
                    break
                    
                order_items_to_create.append(
                    OrderItem(order=order, product_id=prod_id, quantity_requested=qty)
                )
            
            if insufficient_stock:
                # REJECTED status, no stock deducted
                order.status = Order.StatusChoices.REJECTED
                order.save()
            else:
                # Deduct quantities, CONFIRMED status
                for item in items:
                    inv = inventory_map[item['product_id']]
                    inv.quantity -= item['quantity_requested']
                    inv.save()
                
                OrderItem.objects.bulk_create(order_items_to_create)
                order.status = Order.StatusChoices.CONFIRMED
                order.save()

        return Response({
            "order_id": order.id,
            "status": order.status,
            "created_at": order.created_at
        }, status=status.HTTP_201_CREATED)

class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    
    def get_queryset(self):
        store_id = self.kwargs['store_id']
        # Use annotation to avoid N+1 queries when fetching total items
        return Order.objects.filter(store_id=store_id)\
                            .annotate(annotated_total_items=Coalesce(Sum('items__quantity_requested'), 0))\
                            .order_by('-created_at')

