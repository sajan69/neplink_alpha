import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neplink.settings')

app = Celery('neplink')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.update(
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    app.worker_main(['worker', '--pool=gevent', '--concurrency=4'])