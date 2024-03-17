from fastapi import HTTPException
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from request_models.request_models import REmailSchema


def send_email(email_data: REmailSchema, password: str):
    sender_email = os.getenv('EMAIL_LOGIN')
    sender_password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_data.recipient_email
    msg['Subject'] = email_data.subject
    msg.attach(MIMEText(email_data.message.format(password), 'plain'))

    try:
        with smtplib.SMTP('smtp.sibnet.ru', 25) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            return 1
    except Exception as e:
        return e
