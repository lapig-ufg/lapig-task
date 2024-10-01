import os
import email, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from workers.models.email import SendEmail
from workers.render import template
from workers.utils.emial import html_to_text


def send_email(payload: SendEmail):
    try:
        sender_email = os.environ.get('EMAIL_SENDER')
        password = os.environ.get('EMAIL_PASSWORD')
        receiver_email = payload['receiver_email']
        

        message = MIMEMultipart("alternative")
        message["Subject"] = payload['subject']
        message["From"] = sender_email
        message["To"] = receiver_email

        to_render = payload['message']
        html = template.get_template(to_render['template']).render(to_render['content'])

        message.attach(MIMEText(html_to_text(html), "plain"))
        message.attach(MIMEText(html, "html"))

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(os.environ.get('SERVER_EMAIL'), os.environ.get("EMAIL_PORT",465), context=context) as server:
            
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
    except Exception as e:
        raise Exception(f"Error sending email: {e} {sender_email} {password} {receiver_email}")
    return {"status": "Email sent successfully"}


if __name__ == '__main__':
    payload_send_mail ={
     "receiver_email": "devjairomr@gmail.com",
     "subject": "CONCLUÍDA - Requisição de Análise de Geometria (Área)",
     "message":{
        "template":"base.html",
        "content":{
            "title": "CONCLUÍDA - Requisição de Análise de Geometria (Área)",
            "hello": f"Olá, Jairo Matos da Rocja",
            "body": "Conforme solicitação, a análise de dados da área submetida está completa. Você consegue acessar os resultados no link abaixo:",
            "url":"https://atlasdaspastagens.ufg.br/map/123-456-789-000",
            "regards":f"Atenciosamente",
            "team":"Equipe do Atlas das Pastagens do Brasil"
            }
        }}
    send_email(payload_send_mail)