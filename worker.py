import os

from celery import Celery
from workers.send_email import send_email
from workers.gee import task_index_pasture
from app.models.payload import ResultPayload
from celery.utils.log import get_task_logger

from workers.models.email import SendEmail


logger = get_task_logger(__name__)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://quees:6379/0")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://queejobs:6379/0")




@celery.task(name="gee_get_index_pasture",bind=True)
def gee_get_index_pasture(self, payload: ResultPayload):
    result = task_index_pasture(self.request.id, payload)
    payload_send_mail ={
     "receiver_email": payload['user']['email'],
     "subject": "CONCLUÍDA - Requisição de Análise de Geometria (Área)",
     "message":{
        "template":"base.html",
        "content":{
            "title": "CONCLUÍDA - Requisição de Análise de Geometria (Área)",
            "hello": f"Olá, {payload['user']['name']}",
            "body": "Conforme solicitação, a análise de dados da área submetida está completa. Você consegue acessar os resultados no link abaixo:",
            "url":"https://atlasdaspastagens.ufg.br/map/{self.request.id}",
            "regards":f"Atenciosamente",
            "team":"Equipe do Atlas das Pastagens do Brasil"
            }
        }}
    task_send_email.delay(payload_send_mail)
    return result
    
    
@celery.task(name="Send Email")
def task_send_email(payload: SendEmail):
    logger.info(f"Sending email: ")
    return send_email(payload)