import typing

import ee
import orjson
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from google.oauth2 import service_account
from app.config import settings, logger, start_logger

from app.router import created_routes



app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_logger()
    #try:
    #    service_account_file = '/home/lapig/.local/gee.json'
    #    logger.debug(f"Initializing service account {service_account_file}")
    #    credentials = service_account.Credentials.from_service_account_file(
    #        service_account_file,
    #        scopes=["https://www.googleapis.com/auth/earthengine.readonly"],
    #    )
    #    ee.Initialize(credentials)

    #    print("GEE Initialized successfully.")
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail="Failed to initialize GEE")
    

@app.get("/")
def read_root():
    return {"message": "Welcome to the GEE FastAPI"}

app = created_routes(app)
