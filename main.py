
from contextlib import asynccontextmanager
import json

import ee
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import RedirectResponse
from unidecode import unidecode

from app.config import logger, settings, start_logger
from app.router import created_routes

import os 

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_logger()
    def gee_credentials(private_key_file):
        data = json.load(open(private_key_file))
        #logger.info(data)
        gee_account = data['client_email']
        return ee.ServiceAccountCredentials(gee_account, private_key_file)
    
    service_account_file = '/var/sec/gee.json'
    ee.Initialize(gee_credentials(service_account_file))
    yield
    logger.info("Shutting down GEE")
    
app = FastAPI(lifespan=lifespan)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    start_code = exc.status_code
    logger.info(exc)

    if request.url.path.split('/')[1] == 'api':
        try:
            return JSONResponse(
                content={'status_code': start_code, 'message': exc.detail},
                status_code=start_code,
                headers=exc.headers,
            )
        except:
            return JSONResponse(
                content={'status_code': start_code, 'message': exc.detail},
                status_code=start_code
            )
            
    base_url = request.base_url
    if settings.HTTPS:
        base_url = f'{base_url}'.replace('http://', 'https://')
    return {
            'request': request,
            'base_url': base_url,
            'info': '',
            'status': start_code,
            'message': exc.detail,
        }
    


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    try:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            
            content=jsonable_encoder({'detail': unidecode(str(exc.errors())), 'body': unidecode(str(exc.body))}),
            headers={
                'X-Download-Detail': f'{unidecode(str(exc.errors()))}',
                'X-Download-Body': f'{unidecode(str(exc.body))}',
            },
        )
    except Exception as e:
        logger.exception(f'Validation exception: {e} {exc.errors()} {exc.body}')
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({'detail': unidecode(str(exc.errors())), 'body': unidecode(str(exc.body))}),
        )


@app.get("/")
def read_root():
    return RedirectResponse('/redoc')

app = created_routes(app)
