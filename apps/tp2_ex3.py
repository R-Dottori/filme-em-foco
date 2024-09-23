
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Carregando Dados Básicos
salas_rj = pd.read_csv('./data/salas_rj.csv', index_col=0)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
raiz_api = 'https://api-content.ingresso.com/v0/Sessions/city/2/theater/{}'
filme_escolhido = ''


# Título do Exercício 3
st.title('Raspagem de Dados')

# Escolha do bairro e complexo de cinema
st.header('Escolha um bairro e um cinema:')

bairros = sorted(salas_rj['neighborhood'].unique())
filtro_bairro = st.selectbox(label='Selecione um bairro:', options=bairros)
salas_bairro = salas_rj[salas_rj['neighborhood'] == filtro_bairro]['name'].unique()

filtro_cinema = st.selectbox(label='Selecione um complexo de cinema:', options=salas_bairro)
id_cinema = salas_rj[salas_rj['name'] == filtro_cinema]['id'].values[0]


# Resgatando os filmes em cartaz do complexo escolhido
st.header('Escolha um filme:')

try:
    resp = requests.get(
        url=raiz_api.format(id_cinema),
        headers={'user-agent': UA}
        )

    dados_complexo = resp.json()
    filmes_complexo = []

    for dia in dados_complexo:
        for filme in dia['movies']:
            filmes_complexo.append(filme)

    filmes_cartaz = pd.DataFrame(filmes_complexo)
    st.write(filmes_cartaz[['title', 'originalTitle']].drop_duplicates().sort_values('title'))
    filme_escolhido = st.selectbox(label='Selecione um filme:', options=sorted(filmes_cartaz['title'].drop_duplicates()))
except:
    st.error('ERRO! Não encontramos sessões para o complexo escolhido. Por favor, selecione outro cinema.')

# Após escolher um filme, faremos operações de raspagem no portal IMDb
if filme_escolhido != '':
    st.header('IMDb')

    # Selecionando o primeiro resultado da busca, e esperando que seja igual ao filme escolhido
    url_busca = f'https://www.imdb.com/find/?q={filme_escolhido}&ref_=nv_sr_sm'
    resp_imdb = requests.get(
        url=url_busca,
        headers={'user-agent': UA}
        )
    soup_busca = bs(resp_imdb.text)

    # Raspando a página do primeiro resultado da busca
    url_filme = 'https://www.imdb.com/' + soup_busca.select('ul > li > div > div > a')[0]['href']
    resp_filme = requests.get(
        url=url_filme,
        headers={'user-agent': UA}
    )
    soup_filme = bs(resp_filme.text)

    titulo_filme = soup_filme.select('h1 > span')[0].text
    diretor_filme = soup_filme.select('ul > li > div > ul > li > a')[0].text

    # Entrando nas análises dos usuários pro filme e raspando os textos
    url_analises = 'https://www.imdb.com/' + soup_filme.select('section[data-testid="UserReviews"] > div > div > a')[0]['href']
    resp_analises = requests.get(
                    url=url_analises,
                    headers={'user-agent': UA}
                )   
    soup_analises = bs(resp_analises.text)
    analises = ''
    for tag in soup_analises.select('div[class="lister-list"]'):
        for analise in tag.select('div[class="text show-more__control"]'):
            analises += (analise.text.replace('\n', '').replace("'", "")) + ' '

    # Exibindo um pouco da raspagem, o que também confirma se o primeiro resultado da busca estava correto
    st.subheader('Informações do Filme:')
    st.write(f'Título: {titulo_filme}')
    st.write(f'Diretor: {diretor_filme}')

    # Nuvem de Palavras com as análises
    st.subheader('Nuvem de Palavras')
    nuvem = WordCloud().generate(analises)
    plt.figure()
    plt.imshow(nuvem)
    plt.axis('off')
    st.pyplot(plt)
