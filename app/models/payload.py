from pydantic import BaseModel, EmailStr
from typing import List
from pydantic_geojson import FeatureModel, FeatureCollectionModel, PolygonModel

class User(BaseModel):
    name: str
    email: EmailStr


class LapigFeatureModel(FeatureModel):
    properties: dict
    geometry: PolygonModel


class LapigFeatureCollectionModel(FeatureCollectionModel):
    features: List[LapigFeatureModel]

class PayloadSaveGeojson(BaseModel):
    user: User
    geojson: LapigFeatureCollectionModel