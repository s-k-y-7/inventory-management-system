from django.urls import path
from .views import ProductSearchAPIView, AutocompleteAPIView

urlpatterns = [
    path('search/products/', ProductSearchAPIView.as_view(), name='product-search'),
    path('search/suggest/', AutocompleteAPIView.as_view(), name='product-suggest'),
]
