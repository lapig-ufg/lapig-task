from pydantic import BaseModel, EmailStr
class MessageHTML(BaseModel):
    template_name: str
    content: dict

class SendEmail(BaseModel):
    receiver_email: EmailStr
    subject: str
    message: MessageHTML
