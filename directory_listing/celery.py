from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'directory_listing.settings')

app = Celery('directory_listing')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Define custom queue for xls tasks
app.conf.task_queues = {
    'xls_queue': {
        'exchange': 'xls_exchange',
        'routing_key': 'xls.process',
    },
}
