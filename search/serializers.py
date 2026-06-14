from rest_framework import serializers
from products.models import Product

class ProductSearchSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    inventory_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'category_name', 'inventory_quantity']

    def get_inventory_quantity(self, obj):
        store_id = self.context.get('store_id')
        if store_id and hasattr(obj, 'store_quantity'):
            return obj.store_quantity
        return None
