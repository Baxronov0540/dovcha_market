from celery import Celery

from app.config import settings

from app.utils import send_email


celery = Celery(
    __name__,
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


@celery.task(name="send_email_celery")
def send_email_celery(to_email: str, subject: str, body: str):
    send_email(to_email=to_email, subject=subject, body=body)

    return True
