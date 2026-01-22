from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

# Configuración de Jinja2 para plantillas de email
template_env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),  # Busca en la misma carpeta
    autoescape=select_autoescape(['html', 'xml'])
)

# Configuración de FastAPI Mail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(
    email_to: str,
    subject: str = "",
    body: str = "",
    background_tasks: Optional[BackgroundTasks] = None
):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html"
    )
    
    fm = FastMail(conf)
    if background_tasks:
        background_tasks.add_task(fm.send_message, message)
    else:
        await fm.send_message(message)

async def send_reset_password_email(
    email_to: str,
    token: str,
    background_tasks: BackgroundTasks
):
    subject = "Restablecer tu contraseña en OCloud"
    reset_url = f"{settings.SERVER_HOST}/reset-password?token={token}"
    
    # Renderizar la plantilla HTML (solo pasamos reset_url)
    template = template_env.get_template("password_reset.html")
    body = template.render(reset_url=reset_url)
    
    await send_email(
        email_to=email_to,
        subject=subject,
        body=body,
        background_tasks=background_tasks
    )