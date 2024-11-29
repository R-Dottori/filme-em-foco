
from fastapi import APIRouter
from .models import ModeloFilme
import pandas as pd
from typing import List

router = APIRouter()

@router.get('/filmes', response_model=List[ModeloFilme])
async def get_filmes():
    filmes = pd.read_csv('./data/top_250_filmes.csv').to_dict(orient='records')
    return filmes


@router.get('/filmes/genero/{genero}', response_model=List[ModeloFilme])
async def get_filmes_genero(genero: str):
    filmes = pd.read_csv('./data/top_250_filmes.csv')
    filmes_gen = filmes[filmes['genero'].str.contains(genero, case=False)].to_dict(orient='records')
    return filmes_gen


@router.post('/filmes', response_model=ModeloFilme)
async def post_filme(filme: ModeloFilme):
    filmes = pd.read_csv('./data/top_250_filmes.csv')
    novo_filme = pd.DataFrame([filme.dict()])
    filmes = pd.concat([filmes, novo_filme], ignore_index=True)
    filmes.to_csv('./data/top_250_filmes.csv', index=False)
    return filme.dict()
