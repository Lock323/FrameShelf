import smtplib
from email.message import EmailMessage
from celery import Celery
from config import settings


celery = Celery("tasks", broker=settings.redis_url)


def get_email_reset_pw_link(token: dict, user_email: str):
    email = EmailMessage()
    email['Subject'] = 'Reset Password'
    email['From'] = settings.SMTP_USER
    email['To'] = user_email
    email.set_content(
        f"""Hi,
            You requested to reset your password. To set a new password, please click the link below:
            
            http://0.0.0.0:9996/reset_pw/{token['reset_pw_token']}?user_email={user_email}
            
            If you didn’t request a password reset, you can safely ignore this email.
            """
    )
    return email


@celery.task
def send_email_reset_pw_link(token: dict, user_email: str):
    email = get_email_reset_pw_link(token=token, user_email=user_email)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(email)
