from typing import Optional
from pydantic import BaseModel, EmailStr

class UserOauth2(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    realm_roles: list
    client_roles: list
    
    
    
class UserInfo(BaseModel):
    sub: str
    preferred_username: str
    email: Optional[EmailStr] = None
    client_id: Optional[str] = None