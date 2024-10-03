import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


from workers.models.email import SendEmail
from workers.render import template
from workers.utils.emial import html_to_text



def send_email(payload: SendEmail):
    try:
        SERVER_MAIL = os.environ.get('SERVER_EMAIL')
        PORT_EMAIL = os.environ.get("EMAIL_PORT",465)
        
        sender_email = os.environ.get('EMAIL_SENDER')
        password = os.environ.get('EMAIL_PASSWORD')
        receiver_email = payload['receiver_email']
        

        message = MIMEMultipart("alternative")
        message["Subject"] = payload['subject']
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Date"] = formatdate(localtime=True) 

        to_render = payload['message']
        html = template.get_template(to_render['template']).render(to_render['content'])

        message.attach(MIMEText(html_to_text(html), "plain"))
        message.attach(MIMEText(html, "html"))

        # Create secure connection with server and send email
        
        context = ssl.create_default_context()

        try:
            # Conecta ao servidor de e-mail usando TLS
            with smtplib.SMTP(SERVER_MAIL,  PORT_EMAIL) as server:
                server.starttls(context=context)  # Inicia a conexão TLS
                server.login(sender_email, password)  # Faz login no servidor SMTP
                server.sendmail(sender_email, receiver_email, message.as_string())  # Envia o e-mail
                print("E-mail enviado com sucesso!")

        except Exception as e:
            raise Exception(f"Error sending email: {e} \n {sender_email} - {receiver_email}\n {SERVER_MAIL}:{PORT_EMAIL}")
    except Exception as e:
        raise Exception(f"Error sending email: {e}")
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