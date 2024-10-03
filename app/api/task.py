
from pathlib import Path
import shutil
import tempfile
from typing import List
from fastapi.responses import JSONResponse
import geopandas as gpd
from pydantic import EmailStr


from app.models.oauth2 import UserInfo
from app.oauth2 import has_role
from app.utils.file import check_geofiles
from worker import gee_get_index_pasture
from app.models.payload import PayloadSaveGeojson, User
import os

from fastapi import APIRouter, Depends, File, HTTPException, Request, Query, UploadFile
from app.config import logger
from celery.result import AsyncResult

router = APIRouter()


@router.post("/savegeom/geojson" )
async def savegeom_geojson(
    payload: PayloadSaveGeojson,
    crs: int = Query(4326, description="EPSG code for the geometry"),
    user_data: UserInfo = Depends(has_role(['savegeom']))  # This should be a function that retrieves user data from the request.
):
    geojson = payload.dict().get('geojson',gpd.GeoDataFrame())
    user = payload.dict().get('user')
    logger.info(f"Received payload: {geojson}")
    gdf = gpd.GeoDataFrame.from_features(geojson, crs=crs)    
    return __savegeom__(gdf, user, user_data)

@router.post("/savegeom/file" )
async def savegeom_gdf(
    name: str,
    email:EmailStr,
    files: List[UploadFile] = File(...),
    user_data: UserInfo = Depends(has_role(['savegeom']))  # This should be a function that retrieves user data from the request.
):
    return __savegeom__(check_geofiles(files), {'name':name,'email':email}, user_data)
    

            
    

@router.get("/status/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)


def __checkgeom__(gdf: gpd.GeoDataFrame):
    MAXHECTARES = os.environ.get('MAXHECTARES',40_000)
    if gdf.empty:
        raise HTTPException(status_code=400, detail="Empty GeoDataFrame.")
    if len(gdf) > 1:
        raise HTTPException(status_code=400, detail="GeoDataFrame must have only one geometry.")
    if gdf.geometry.type[0] != "Polygon":
        raise HTTPException(status_code=400, detail="Geometry must be a Polygon.")
    if gdf.to_crs(5880).area.iloc[0] / 10_000 > MAXHECTARES:
        raise HTTPException(status_code=400, detail=f"Geometry area must be less than {MAXHECTARES} hectares.")
    logger.info('Geometry is valid')
    return gdf.to_crs(4326).to_geo_dict()
    


def __savegeom__(gdf: gpd.GeoDataFrame, user: User,user_data: UserInfo):
    dict_payload = {
        'user':user,
        'geojson':__checkgeom__(gdf),
        'request_user': user_data
    }
    logger.info(f"Starting task with payload: {dict_payload}")
    task = gee_get_index_pasture.delay(dict_payload)
    return JSONResponse({"task_id": task.id})