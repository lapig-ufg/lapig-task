import shutil
import tempfile
from zipfile import ZipFile
from pathlib import Path
from fastapi import HTTPException
import geopandas as gpd
from app.config import logger

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
    if file.suffix in [
        ".shp",  # Geometria dos vetores
        ".shx",  # Índice de geometria
        ".dbf",  # Dados tabulares
        ".prj",  # Sistema de coordenadas e projeção
        ".cpg",  # Codificação de caracteres
        ".sbn",  # Índice espacial
        ".sbx",  # Arquivo auxiliar para índice espacial
        ".xml",  # Metadados em formato XML
        ".qix",  # Índice espacial (gerado por software)
        ".aih",  # Índice de atributos para .dbf
        ".ain",  # Arquivo auxiliar para índice de atributos
        ".qmd"   # Extensão adicional (se aplicável)
    ]:
        return True
    raise HTTPException(status_code=415, detail=f'Invalid file type: {file.suffix}')


def check_geofiles(files):
    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.info(f"Saving files to {tmpdirname}")
        logger.info(files)
        if len(files) == 1:
            valid_file_geo(files[0].content_type)
            file = files[0]
        else:
            extensions = []
            for f in files:
                valid_file_geo(f.content_type)
                valid_extension_shp(Path(f.filename))
                extensions.append(Path(f.filename).suffix)
                with open(f'{tmpdirname}/{f.filename}', 'wb') as buffer:
                    shutil.copyfileobj(f.file, buffer)
            minal_shape =set(['.shp', '.shx', '.dbf', '.prj']) - set(extensions)
            if len(minal_shape) > 0:
                raise HTTPException(status_code=400, detail=f'Missing files: {minal_shape}')
            file = str(get_geofile(tmpdirname))  
        return read_file(file)


def read_kml(file):
    import fiona
    try:
        return gpd.read_file(file, driver='KML')
    except Exception as e:
        gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
        return gpd.read_file(file, driver='KML')
    
    
def read_kmz(file):
    import fiona
    with tempfile.TemporaryDirectory() as tmpdirname:
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
        if file.suffix in ['.shp']:
            return file


def read_file(file):
    if isinstance(file, str):
        gdf = gpd.read_file(file)
    else:
        match Path(file.filename).suffix.capitalize():
            case '.kml':
                gdf = read_kml(file.file)
            case '.kmz':
                gdf = read_kmz(file.file)
            case  _:
                gdf = read_gpd(file.file) 
    
    return gdf