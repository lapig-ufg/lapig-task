from pydantic import BaseModel, EmailStr
from typing import List
from app.models.oauth2 import UserInfo
from pydantic_geojson import FeatureModel, FeatureCollectionModel, PolygonModel
from datetime import datetime

class User(BaseModel):
    name: str
    email: EmailStr


class LapigFeatureModel(FeatureModel):
    properties: dict
    geometry: PolygonModel


class LapigFeatureCollectionModel(FeatureCollectionModel):
    features: List[LapigFeatureModel]


class ResultPayload(BaseModel):
    user: User
    created_at: datetime = datetime.now(tz=datetime.timezone.utc)
    geojson: LapigFeatureCollectionModel
    request_user: UserInfo
class PayloadSaveGeojson(BaseModel):
    user: User
    geojson: LapigFeatureCollectionModel
    model_config = {
      "user": {
        "name": "Jairo Matos da Rocha",
        "email": "devjairomr@gmail.com"
      },
      "geojson": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "properties": {},
          "geometry": {
            "coordinates": [
              [
                [
                  -49.271489630116974,
                  -16.600834057263143
                ],
                [
                  -49.271489630116974,
                  -16.613595063494913
                ],
                [
                  -49.25488564150811,
                  -16.613595063494913
                ],
                [
                  -49.25488564150811,
                  -16.600834057263143
                ],
                [
                  -49.271489630116974,
                  -16.600834057263143
                ]
              ]
            ],
            "type": "Polygon"
          }
        }
      ]
    }
    }