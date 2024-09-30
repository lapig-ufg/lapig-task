from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import requests


from fastapi import APIRouter, Depends, HTTPException


from app.oauth2 import CLIENT_ID, CLIENT_SECRET, TOKEN_URL


router = APIRouter()


# Modelo de resposta para o token
class Token(BaseModel):
    access_token: str
    token_type: str

# Rota de login para obter o token de acesso
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Dados para a requisição ao Keycloak
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'password',
        'username': form_data.username,
        'password': form_data.password
    }

    # Requisição ao Keycloak para obter o token
    response = requests.post(TOKEN_URL, data=payload)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Username or password incorrect"
        )

    token_data = response.json()
    return {
        "access_token": token_data["access_token"],
        "token_type": "bearer"
    }
    

