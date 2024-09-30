from fastapi.responses import JSONResponse
import geopandas as gpd
import ee

from app.models.oauth2 import UserInfo
from app.oauth2 import has_role
import os

from fastapi import APIRouter, Depends,  HTTPException, Request, Query
from app.config import logger

router = APIRouter()


@router.get("/public" )
def public():
    return JSONResponse({"message": "public"})



@router.get("/privete" )
async def privete(
    request: Request,
    user_data: UserInfo = Depends(has_role(['savegeom']))  # This should be a function that retrieves user data from the request.
):  
    """ Essa rota e privada e o usuario precisa da permição savegeom par acessar

    Args:
        request (Request): Request do FastAPI
        user_data (UserInfo, optional): Dados basico do usurio que pediu a rota

    Returns:
        _type_: _description_
    """
    return JSONResponse({"message": "privete", "data": user_data})