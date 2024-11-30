
from fastapi import APIRouter, HTTPException
from .models import ModeloFilme, ModeloAnalise
import pandas as pd
from typing import List
import ast
from transformers import pipeline

router = APIRouter()

@router.get('/filmes', response_model=List[ModeloFilme])
async def get_filmes():
    try:
        filmes = pd.read_csv('./data/top_250_filmes.csv').to_dict(orient='records')
        return filmes
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Base de dados não encontrada.')
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail='Base de dados está vazia.')


@router.get('/filmes/genero/{genero}', response_model=List[ModeloFilme])
async def get_filmes_genero(genero: str):
    try:
        filmes = pd.read_csv('./data/top_250_filmes.csv')
        filmes_gen = filmes[filmes['genero'].str.contains(genero, case=False)]
        if filmes_gen.empty:
            raise HTTPException(status_code=404, detail='Não há nenhum filme desse gênero.')
        return filmes_gen.to_dict(orient='records')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Base de dados não encontrada.')
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail='Base de dados está vazia.')


@router.post('/filmes', response_model=ModeloFilme)
async def post_filme(filme: ModeloFilme):
    try:
        filmes = pd.read_csv('./data/adicionar_filmes.csv')
        novo_filme = pd.DataFrame([filme.dict()])
        if filmes[['titulo', 'ano']].apply(lambda x: x['titulo'] == novo_filme['titulo'][0]
                                                    and x['ano'] == novo_filme['ano'][0], axis=1).any():
            raise HTTPException(status_code=400, detail='O filme já existe na base de dados.')
        filmes = pd.concat([filmes, novo_filme], ignore_index=True)
        filmes.to_csv('./data/adicionar_filmes.csv', index=False)
        return filme.dict()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Base de dados não encontrada.')
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail='Base de dados está vazia.')



# NOVAS ROTAS
@router.post('/analises/classificacao')
async def post_classificacao(body: ModeloAnalise):
    try:
        modelo_sentimentos = pipeline('text-classification',
                                model='lvwerra/distilbert-imdb',
                                tokenizer='distilbert/distilbert-base-uncased-finetuned-sst-2-english',
                                truncation=True,
                                padding='max_length',
                                max_length=512)
        resultado = modelo_sentimentos(body.analise)[0]['label']
        return {'tarefa': 'classificação', 'analise': body.analise, 'resultado': resultado}
    except:
        raise HTTPException(status_code=503, detail='Erro ao carregar o modelo.')


@router.post('/analises/resumo')
async def post_resumo(body: ModeloAnalise):
    try:
        modelo_resumo = pipeline('summarization',
                            model='abhiramd22/t5-base-finetuned-to-summarize-movie-reviews')

        resumo = modelo_resumo(body.analise)[0]['summary_text']
        return {'tarefa': 'resumo', 'analise': body.analise, 'resumo': resumo}
    except:
        raise HTTPException(status_code=503, detail='Erro ao carregar o modelo.')
