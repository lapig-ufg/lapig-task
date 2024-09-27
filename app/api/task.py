
from fastapi.responses import JSONResponse
import geopandas as gpd
from worker import gee_get_index_pasture
from app.models.payload import PayloadSaveGeojson

from fastapi import APIRouter, HTTPException, Request, Query
from app.config import logger
from celery.result import AsyncResult
from pydantic import UUID4

router = APIRouter()

@router.post("/savegeom")
async def savegeom(
    payload: PayloadSaveGeojson,
    request: Request,
    crs: int = Query(4326, description="EPSG code for the geometry"),
    
):
    MAX_HECTARES = 40_000
    geojson = payload.dict().get('geojson',gpd.GeoDataFrame())
    logger.info(f"Received payload: {geojson}")
    try:
        gdf = gpd.GeoDataFrame.from_features(geojson, crs=crs)
        if gdf.empty or len(gdf) > 1:
            return HTTPException(status_code=400, detail="Empty GeoDataFrame or more than one feature.")
        if gdf.geometry.type[0] != "Polygon":
            return HTTPException(status_code=400, detail="Geometry must be a Polygon.")
        if gdf.to_crs(5880).area.iloc[0] / 10_000 > MAX_HECTARES:
            return HTTPException(status_code=400, detail=f"Geometry area must be less than {MAX_HECTARES} hectares.")
        logger.info('Geometry is valid')
        try:
            task = gee_get_index_pasture.delay(payload.dict())
        except Exception as e:
            logger.exception(f"Failed to create task: {e}")
            raise HTTPException(status_code=400, detail="Failed to create task.")
    except Exception as e:
        logger.error(f"{e}")
        raise HTTPException(status_code=400, detail=e)
    
    return JSONResponse({"task_id": task.id})

@router.get("/status/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)