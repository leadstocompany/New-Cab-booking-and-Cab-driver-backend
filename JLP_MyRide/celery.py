import os
# Configure Django to use Celery
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JLP_MyRide.settings')

app = Celery('JLP_MyRide')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()