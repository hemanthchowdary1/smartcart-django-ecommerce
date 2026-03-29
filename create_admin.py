import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User

username = "admin"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, "admin@gmail.com", password)
    print("Superuser created")
else:
    print("User already exists")