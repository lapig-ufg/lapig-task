import shutil
import tempfile
from zipfile import ZipFile
from pathlib import Path
from fastapi import HTTPException
import geopandas as gpd
from app.config import logger

MINIMAL_SHP_SUFFIX = [
        ".shp",  # Geometria dos vetores
        ".shx",  # Índice de geometria
        ".dbf",  # Dados tabulares
        ".prj",  # Sistema de coordenadas e projeção
    ]
FULL_SHP =  [
        *MINIMAL_SHP_SUFFIX,
        ".cpg",  # Codificação de caracteres
        ".sbn",  # Índice espacial
        ".sbx",  # Arquivo auxiliar para índice espacial
        ".xml",  # Metadados em formato XML
        ".qix",  # Índice espacial (gerado por software)
        ".aih",  # Índice de atributos para .dbf
        ".ain",  # Arquivo auxiliar para índice de atributos
        ".qmd"   # Extensão adicional (se aplicável)
    ]

ZIP_READ = [
    '.kml',
    '.kmz',
    '.gpkg',
    '.geojson',
    '.topojson',
    '.shp'
]


GEOFILES = [
    '.zip',
    '.kml',
    '.kmz',
    '.gpkg',
    '.geojson',
    '.topojson',
    *FULL_SHP
]


def valid_file_geo(content_type):
    
    if content_type in [
        'application/text',
        'application/xml',
        'text/plain',
        'application/geo+json',
        'application/geopackage+sqlite3',
        'application/octet-stream',
        'application/vnd.google-earth.kml+xml',
        'application/vnd.google-earth.kmz',
        'application/x-dbf',
        'application/x-esri-crs',
        'application/x-esri-shape',
        'application/zip'
    ]:
        return True
    raise HTTPException(status_code=415, detail=f'Invalid file type: {content_type}')

def valid_extension_shp(file):
    if file.suffix.lower() in FULL_SHP:
        return file.suffix.lower()
    raise HTTPException(status_code=415, detail=f'Invalid file type: {file.suffix.lower()}')

def valid_extension(file):
    if file.suffix.lower() in GEOFILES:
        return file.suffix.lower()
    raise HTTPException(status_code=415, detail=f'Invalid file type: {file.suffix.lower()}')


def check_geofiles(files):
    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.info(f"Saving files to {tmpdirname}")
        logger.info(files)
        if len(files) == 1:
            filename = Path(files[0].filename)
            valid_file_geo(files[0].content_type)
            valid_extension(filename)
            if filename.suffix.lower() in FULL_SHP:
                minal_shape = set(MINIMAL_SHP_SUFFIX) - set([filename.suffix.lower()])
                raise HTTPException(status_code=400, detail=f'Missing files: {minal_shape}')
            
            file = files[0]
        else:
            extensions = []
            for f in files:
                valid_file_geo(f.content_type)
                valid_extension_shp(Path(f.filename))
                extensions.append(Path(f.filename).suffix.lower())
                with open(f'{tmpdirname}/{f.filename}', 'wb') as buffer:
                    shutil.copyfileobj(f.file, buffer)
            minal_shape = set(MINIMAL_SHP_SUFFIX) - set(extensions)
            if len(minal_shape) > 0:
                raise HTTPException(status_code=400, detail=f'Missing files: {minal_shape}')
            file = str(get_geofile(tmpdirname))  
        return read_file(file, tmpdirname)


def read_kml(file):
    import fiona
    try:
        return gpd.read_file(file, driver='KML')
    except Exception as e:
        gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
        return gpd.read_file(file, driver='KML')
    
    
def read_kmz(file,tmpdirname):
    import fiona
    kmz = ZipFile(file, 'r')
    kmz.extract('doc.kml',tmpdirname)
    try:
        gdf = gpd.read_file(f'{tmpdirname}/doc.kml')
    except Exception as e:
        gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
        gdf = gpd.read_file(f'{tmpdirname}/doc.kml')
            
    return gdf
    
def read_gpd(file):
    return gpd.read_file(file) 


def get_geofile(dirname):
    for file in Path(dirname).glob('*'):
        if file.suffix.lower() in ZIP_READ:
            return file


def read_file(file,tmpdirname):
    if isinstance(file, str):
        gdf = gpd.read_file(file)
    else:
        match Path(file.filename).suffix.lower():
            case '.kml':
                gdf = read_kml(file.file)
            case '.kmz':
                gdf = read_kmz(file.file, tmpdirname)
            case '.zip':
                dots = []
                with ZipFile(file.file) as zfile:
                    for f in zfile.namelist():
                        logger.info(f'd {f}')
                        dots.append(valid_extension(Path(f)))
                    zfile.extractall(tmpdirname)
                dots = [f for f in dots if f in ZIP_READ] 
                if len(dots) == 0 or len(dots) > 1:
                    raise HTTPException(status_code=400, detail='No valid files in the ZIP archive')
                filename = get_geofile(tmpdirname)
                
                match Path(filename).suffix.lower():
                    case '.kml':
                        gdf = read_kml(filename)
                    case '.kmz':
                        gdf = read_kmz(filename)
                    case _:
                        gdf = gpd.read_file(filename)
            case  _:
                gdf = read_gpd(file.file) 
    
    return gdf