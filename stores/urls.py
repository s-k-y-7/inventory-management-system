from django.urls import path
from .views import InventoryListingAPIView, OrderListAPIView

urlpatterns = [
    path('<int:store_id>/inventory/', InventoryListingAPIView.as_view(), name='store-inventory-list'),
    path('<int:store_id>/orders/', OrderListAPIView.as_view(), name='store-order-list'),
]
