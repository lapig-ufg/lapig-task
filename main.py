
from contextlib import asynccontextmanager
import json
import os

import ee
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import RedirectResponse
from unidecode import unidecode
from fastapi.middleware.cors import CORSMiddleware

from app.config import logger, settings, start_logger
from app.router import created_routes
from app.utils.cors import allow_origins, origin_regex


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

# Configurações CORS com expressões regulares para subdomínios dinâmicos
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # Lista de origens estáticas (deixe vazio se estiver usando regex)
    allow_methods=["*"],  # Métodos permitidos
    allow_headers=["*"],  # Cabeçalhos permitidos
    allow_credentials=True,  # Permite o envio de cookies/credenciais
    allow_origin_regex=origin_regex,
    expose_headers=["X-Response-Time"],  # Cabeçalhos expostos
    max_age=3600,  # Tempo máximo para cache da resposta preflight
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    start_code = exc.status_code
    loggger.error(str(exc.detail))
    if request.url.path.split('/')[1] == 'api':
        try:
            return JSONResponse(
                content={'status_code': start_code, 'message': str(exc.detail)},
                status_code=start_code,
                headers=exc.headers,
            )
        except:
            return JSONResponse(
                content={'status_code': start_code, 'message': str(exc.detail)},
                status_code=start_code
            )
            
    base_url = request.base_url
    if os.environ.get('HTTPS',False):
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
