from django.core.management.base import BaseCommand
from faker import Faker
import random

from store.models import Product, Category

fake = Faker()

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        categories = Category.objects.all()

        if not categories:
            print("Create categories first.")
            return

        for i in range(40):

            Product.objects.create(
                name=random.choice([
                    "Gaming Laptop",
                    "Wireless Earbuds",
                    "Smart Watch",
                    "Mechanical Keyboard",
                    "4K Smart TV",
                    "Bluetooth Speaker",
                    "Gaming Mouse",
                    "iPhone Case",
                    "USB-C Hub",
                    "Portable SSD"
                ]),
                description=fake.text(max_nb_chars=200),
                price=random.randint(500, 150000),
                stock=random.randint(5, 100),
                category=random.choice(categories)
)

print("✅ Fake products created!")