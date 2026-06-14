from rest_framework import generics
from rest_framework.response import Response
from django.core.cache import cache
from .models import Inventory
from .serializers import InventorySerializer
from orders.views import OrderListAPIView

class InventoryListingAPIView(generics.ListAPIView):
    serializer_class = InventorySerializer

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        return Inventory.objects.filter(store_id=store_id)\
                                .select_related('product', 'product__category')\
                                .order_by('product__title')

    def list(self, request, *args, **kwargs):
        store_id = self.kwargs['store_id']
        cache_key = f'inventory_store_{store_id}'
        
        # 1. Check if data is already in Redis cache
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
            
        # 2. If not in cache, query the database normally
        response = super().list(request, *args, **kwargs)
        
        # 3. Save the result into Redis cache for 15 minutes
        cache.set(cache_key, response.data, timeout=60 * 15)
        
        return response

