from rest_framework import generics
from .models import Inventory
from .serializers import InventorySerializer
from orders.views import OrderListAPIView

class InventoryListingAPIView(generics.ListAPIView):
    serializer_class = InventorySerializer

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        # select_related avoids N+1 for product and category
        return Inventory.objects.filter(store_id=store_id)\
                                .select_related('product', 'product__category')\
                                .order_by('product__title')

