from rest_framework.test import APITestCase
from rest_framework import status
from stores.models import Store, Inventory
from products.models import Product, Category
from orders.models import Order, OrderItem
from django.urls import reverse

class OrderAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(title='Phone', price=500.0, category=self.category)
        self.store = Store.objects.create(name='Tech Store', location='NY')
        self.inventory = Inventory.objects.create(store=self.store, product=self.product, quantity=10)

    def test_create_order_success(self):
        url = reverse('order-create')
        data = {
            'store_id': self.store.id,
            'items': [{'product_id': self.product.id, 'quantity_requested': 2}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'CONFIRMED')
        
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 8)

    def test_create_order_insufficient_stock(self):
        url = reverse('order-create')
        data = {
            'store_id': self.store.id,
            'items': [{'product_id': self.product.id, 'quantity_requested': 20}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'REJECTED')
        
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 10)

    def test_list_inventory(self):
        url = reverse('store-inventory-list', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product_title'], 'Phone')

    def test_search_api(self):
        url = reverse('product-search') + '?q=Phone'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
        
    def test_autocomplete_api(self):
        url = reverse('product-suggest') + '?q=Pho'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
