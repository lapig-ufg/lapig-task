from fastapi import APIRouter, HTTPException
import os
from pymongo import MongoClient
from pydantic import UUID4
router = APIRouter()


@router.get("/{task_id}")
async def result_pasture(task_id):
    with MongoClient(os.environ.get("MONGOURI", "mongodb://mongodbjobs:27017")) as cliente:
    # Seleciona o banco de dados e a coleção
        banco_de_dados = cliente['lapig-task']
        colecao = banco_de_dados['results']
        
        data = colecao.find_one({'_id':task_id})
        
        return data
        