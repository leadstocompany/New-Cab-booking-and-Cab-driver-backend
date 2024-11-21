import os
# Configure Django to use Celery
from celery import Celery
# from __future__ import absolute_import, unicode_literals


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JLP_MyRide.settings')

app = Celery('JLP_MyRide')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicitly set broker connection retry settings
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()