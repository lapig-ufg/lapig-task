import os

from celery import Celery
from workers.gee import task_index_pasture
from app.models.payload import ResultPayload
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://quees:6379/0")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://queejobs:6379/0")




@celery.task(name="gee_get_index_pasture",bind=True)
def gee_get_index_pasture(self, payload: ResultPayload):
    return task_index_pasture(self.request.id, payload)
    
    