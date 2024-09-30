import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from workers.models.email import SendEmail
from workers.render import template
from workers.utils.emial import html_to_text


def send_email(payload: SendEmail):
    
    sender_email = os.environ.get('EMAIL_SENDER')
    password = os.environ.get('EMAIL_PASSWORD')
    receiver_email = payload['receiver_email']
    

    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender_email
    message["To"] = receiver_email

    to_render = payload['message']
    html = template.get_template(to_render['templet_name']).render(to_render['content'])

    message.attach(MIMEText(html_to_text(html), "plain"))
    message.attach(MIMEText(html, "html"))

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(os.environ.get('SERVER_EMAIL'), 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )