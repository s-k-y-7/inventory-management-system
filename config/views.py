from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root that lists all available endpoints in the project.
    Since some endpoints require a store_id, we provide an example using store_id=1.
    """
    return Response({
        'Create Order (POST)': reverse('order-create', request=request, format=format),
        'Store Inventory (GET) [Example Store 1]': reverse('store-inventory-list', kwargs={'store_id': 1}, request=request, format=format),
        'Store Orders (GET) [Example Store 1]': reverse('store-order-list', kwargs={'store_id': 1}, request=request, format=format),
        'Product Search (GET)': reverse('product-search', request=request, format=format),
        'Product Autocomplete Suggest (GET)': reverse('product-suggest', request=request, format=format),
    })
