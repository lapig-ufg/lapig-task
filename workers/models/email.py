from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailResponse(BaseModel):
    title: str
    hello : Optional[str]
    body: str
    url: Optional[str]
    regards: Optional[str]
    team: str


class MessageHTML(BaseModel):
    template_name: str
    content: dict

class SendEmail(BaseModel):
    receiver_email: EmailStr
    subject: str
    message: MessageHTML
