from typing import List
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID # pip require python-keycloak
from fastapi import Security, HTTPException, status,Depends
from pydantic import Json
from app.models.oauth2 import UserInfo, UserOauth2

import os
from app.config import logger

URLKEYCLOAK = f"{os.environ.get('SERVER_URL')}/realms/{os.environ.get('REALM')}/"


TOKEN_URL = f"{URLKEYCLOAK}protocol/openid-connect/token"
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
AUTHORIZATIONURL=f"{URLKEYCLOAK}protocol/openid-connect/auth"
CERTS=f"{URLKEYCLOAK}protocol/openid-connect/certs"
REALM=os.environ.get('REALM')

# This is used for fastapi docs authentification
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    #refreshUrl=TOKEN_URL,
    authorizationUrl=AUTHORIZATIONURL, # https://sso.example.com/auth/
    tokenUrl=TOKEN_URL, # https://sso.example.com/auth/realms/example-realm/protocol/openid-connect/token
)

# This actually does the auth checks
# client_secret_key is not mandatory if the client is public on keycloak
keycloak_openid = KeycloakOpenID(
    server_url=os.environ.get('SERVER_URL'), # https://sso.example.com/auth/
    client_id=CLIENT_ID, # backend-client-id
    realm_name=REALM, # example-realm
    client_secret_key=CLIENT_SECRET, # your backend client secret
    verify=True
)





async def get_idp_public_key():
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{keycloak_openid.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )

# Get the payload/token from keycloak
async def get_payload(token: str = Security(oauth2_scheme)) -> dict:
    key= await get_idp_public_key()
    try:
        
        return keycloak_openid.decode_token(
            token
        )
    except Exception as e:
        logger.exception(f"Error decoding token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e), # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def get_info_user(payload) -> UserInfo:
    if not payload.get('email', None) is None:
        return {
            'sub': payload['sub'],
            'preferred_username': payload['preferred_username'],
            'email': payload['email']
        }
    else:
        return {
            'sub': payload['sub'],
            'preferred_username': payload['preferred_username'],
            'client_id': payload.get('client_id')
        }
        


def has_role(role:List[str]) -> UserInfo:
    logger.info(f"has_role {role}")
    async def check_role(payload: dict = Depends(get_payload)):
   
        if not payload.get("resource_access", {}).get("app_task", {}):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized to access this resource",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not any([user_role in role for user_role in payload.get("resource_access", {}).get("app_task", {}).get("roles", [])]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges to access this resource",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return get_info_user(payload)
    return check_role


# Get user infos from the payload
async def get_user_info(payload: dict = Depends(get_payload)) -> UserOauth2:
    try:
        return UserOauth2(
            id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            first_name=payload.get("given_name"),
            last_name=payload.get("family_name"),
            realm_roles=payload.get("realm_access", {}).get("roles", []),
            client_roles=payload.get("realm_access", {}).get("roles", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e), # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
