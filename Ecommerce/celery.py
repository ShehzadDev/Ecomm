import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ecommerce.settings")

app = Celery("Ecommerce")

# Use a string here so the worker doesn't have to serialize the configuration object to child processes
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks in all registered Django apps
app.autodiscover_tasks()
