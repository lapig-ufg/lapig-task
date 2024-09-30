from workers.utils.gee2chat import get_chat_pasture, get_chat_pasture_vigor
from app.models.payload import ResultPayload
from celery.utils.log import get_task_logger
from pymongo import MongoClient
import ee
import geemap
import json

logger = get_task_logger(__name__)

def task_index_pasture(task_id: str, payload: ResultPayload):
    geojson = payload.get('geojson')
    def gee_credentials(private_key_file):
        data = json.load(open(private_key_file))
        #logger.info(data)
        gee_account = data['client_email']
        return ee.ServiceAccountCredentials(gee_account, private_key_file)
    
    service_account_file = '/var/sec/gee.json'
    
    
    ee.Initialize(gee_credentials(service_account_file))
    
    geometry = geemap.geojson_to_ee(geojson)
    
    exprecion = {'L8':{
        'CAI':    "(b('SR_B7') / b('SR_B6'))",
        'NDVI':   "(b('SR_B5') - b('SR_B4')) / (b('SR_B5') + b('SR_B4'))",
        'NDWI':   "(b('SR_B5') - b('SR_B6')) / (b('SR_B5') + b('SR_B6'))",
        'eq':2720,
        'bands': ["B3","B4","B5","B6","B7","NDVI","NDWI","CAI"]
      },
    'L5_7':{
      'CAI':  "(b('SR_B7') / b('SR_B5'))",
      'NDVI': "(b('SR_B4') - b('SR_B3')) / (b('SR_B4') + b('SR_B3'))",
      'NDWI': "(b('SR_B4') - b('SR_B5')) / (b('SR_B4') + b('SR_B5'))",
      'bands':["B2","B3","B4","B5","B7","NDVI","NDWI","CAI"],
      'eq':672
    }}
    
    pastue_years = []
    pastue_vigor_years = []
    for i in range(1985,2024):
        pastue_years.append(ee.Image(f'users/lapig/pasture_col09/pasture_br_Y{i}_COL9_atlas').set('year',i))
        if i >= 2000:
            pastue_vigor_years.append(ee.Image(f'users/lapig/pasture_vigor_col09/cvp_pasture_br_LAPIG_Y{i}_ATLAS').set('year',i))

    pasture = ee.ImageCollection.fromImages(pastue_years)
    pasture_vigor = ee.ImageCollection.fromImages(pastue_vigor_years)

    # Applies scaling factors.
    def applyScaleFactors(image):
        return image.select('SR_B.').multiply(0.0000275).add(-0.2);


    ls05 = ee.ImageCollection("LANDSAT/LT05/C02/T1_L2")
    ls07 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
    ls08 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    
    
    def index_landsat57(image):
        ndvi = image.expression(exprecion['L5_7']['NDVI']).rename('NDVI')
        cai = image.expression(exprecion['L5_7']['CAI']).rename('CAI')
        ndwi = image.expression(exprecion['L5_7']['NDWI']).rename('NWDI')
        return image.addBands([ndvi,cai,ndwi])
    
    def index_landsat8(image):
        ndvi = image.expression(exprecion['L8']['NDVI']).rename('NDVI')
        cai = image.expression(exprecion['L8']['CAI']).rename('CAI')
        ndwi = image.expression(exprecion['L8']['NDWI']).rename('NWDI')
        return image.addBands([ndvi,cai,ndwi])

    def get_index(year):
        return ee.Algorithms.If(year.gte(1985).And(year.lt(2012)),
            (ls05.filterDate(ee.String(year).cat('-01-01'),ee.String(year).cat('-12-31'))
             .filterBounds(geometry)
             .map(applyScaleFactors).map(index_landsat57).mean().set('year',year).set('sat',5)),
        ee.Algorithms.If(year.gte(2012).And(year.lt(2013)),
            (ls07.filterDate(ee.String(year).cat('-01-01'),ee.String(year).cat('-12-31'))
             .filterBounds(geometry)
             .map(applyScaleFactors).map(index_landsat57).mean().set('year',year).set('sat',7)),
            
        (ls08.filterDate(ee.String(year).cat('-01-01'),ee.String(year).cat('-12-31'))
             .filterBounds(geometry)
             .map(applyScaleFactors).map(index_landsat8).mean().set('year',year).set('sat',8))
        )
        )
    
    def get_precipitation(year):
        dataset = (ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
                   .filterBounds(geometry)
                   .filter(ee.Filter.date(ee.String(year).cat('-01-01'),ee.String(year).cat('-12-31')))
        )
        return dataset.select('precipitation').sum().set('year',year)    

    def pasture_reduce(img):
        year = img.get('year') 
        index = ee.Image(get_index(ee.Number(year))).updateMask(img)
        precipitation = ee.Image(get_precipitation(ee.Number(year))).updateMask(img)
        
        
        area_pixel = ee.Image.pixelArea().divide(10000).updateMask(img).rename('area_ha')
        
        result = area_pixel.reduceRegion(**{
            "reducer": ee.Reducer.sum(),
            "geometry": geometry, 
            "scale": 30, 
            "maxPixels": 10e9 })
            
        result_index = index.select(["NDVI","CAI","NWDI"]).addBands(precipitation).reduceRegion(**{
            "reducer": ee.Reducer.mean(), 
            "geometry": geometry, 
            "scale": 30, 
            "maxPixels": 10e9 })
        
        
        return ee.Feature(None,ee.Dictionary({
            "area_ha":result.get('area_ha'),
            "indexs":result_index,
            "year":year}))
        
    def pasute_vigor_reduce(img):
        year = img.get('year') 
        index = ee.Image(get_index(ee.Number(year))).updateMask(img)
        
        area_pixel = ee.Image.pixelArea().divide(10000).rename('area_ha').addBands(img.select('b1'))
        result = area_pixel.reduceRegion(**{
            "reducer": ee.Reducer.sum().group(**{
                "groupField": 1,
                "groupName": 'class',
            }), 
            "geometry": geometry, 
            "scale": 30, 
            "maxPixels": 10e9 })
            
        result_ndvi = index.select('NDVI').addBands(img.select('b1')).reduceRegion(**{
            "reducer": ee.Reducer.mean().group(**{
                "groupField": 1,
                "groupName": 'class',
            }),
            "geometry": geometry, 
            "scale": 30, 
            "maxPixels": 10e9 })
        
        result_cai = index.select('CAI').addBands(img.select('b1')).reduceRegion(**{
            "reducer": ee.Reducer.mean().group(**{
                "groupField": 1,
                "groupName": 'class',
            }),
            "geometry": geometry, 
            "scale": 30, 
            "maxPixels": 10e9 })
        
        result_ndwi = index.select('NWDI').addBands(img.select('b1')).reduceRegion(**{
            "reducer": ee.Reducer.mean().group(**{
                "groupField": 1,
                "groupName": 'class',
            }),
            "geometry": geometry, 
            "scale": 30, 
            "maxPixels": 10e9 })
        
        
        
        return ee.Feature(None,ee.Dictionary({
            "area_ha":result,
            "ndiv":result_ndvi,
            "cai":result_cai,
            "ndwi":result_ndwi,
            "year":year
            
        }))
    

    result_pasture = pasture.map(pasture_reduce)

    result_pasture_vigor = pasture_vigor.map(pasute_vigor_reduce)
    
    result = {
        '_id':task_id,
        **payload,
        'pasture':get_chat_pasture(result_pasture.getInfo()['features']), 
        'pasture_vigor':get_chat_pasture_vigor(result_pasture_vigor.getInfo()['features']),
        }
    
    with MongoClient(os.environ.get("MONGOURI", "mongodb://mongodbjobs:27017")) as cliente:
    # Seleciona o banco de dados e a coleção
        banco_de_dados = cliente['lapig-task']
        colecao = banco_de_dados['results']

        # Insere o documento na coleção
        resultado = colecao.insert_one(result)
    return result