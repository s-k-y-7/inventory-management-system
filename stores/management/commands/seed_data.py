import os
from django.core.management.base import BaseCommand
from products.models import Category, Product
from stores.models import Store, Inventory
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seed database with dummy data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        self.stdout.write('Deleting old data...')
        Inventory.objects.all().delete()
        Store.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        fake.unique.clear()

        self.stdout.write('Seeding Categories...')
        categories = []
        for _ in range(15):
            cat, _ = Category.objects.get_or_create(name=fake.unique.word().capitalize())
            categories.append(cat)
            
        self.stdout.write('Seeding Products...')
        products = []
        for _ in range(1000):
            prod = Product(
                title=fake.catch_phrase(),
                description=fake.text(),
                price=round(random.uniform(5.0, 500.0), 2),
                category=random.choice(categories)
            )
            products.append(prod)
        Product.objects.bulk_create(products)
        products = list(Product.objects.all())
        
        self.stdout.write('Seeding Stores...')
        stores = []
        for _ in range(25):
            store = Store(
                name=fake.company(),
                location=fake.city()
            )
            stores.append(store)
        Store.objects.bulk_create(stores)
        stores = list(Store.objects.all())
        
        self.stdout.write('Seeding Inventory...')
        inventory_items = []
        for store in stores:
            store_products = random.sample(products, random.randint(300, 500))
            for prod in store_products:
                inventory_items.append(
                    Inventory(
                        store=store,
                        product=prod,
                        quantity=random.randint(0, 100)
                    )
                )
        Inventory.objects.bulk_create(inventory_items, batch_size=5000)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
