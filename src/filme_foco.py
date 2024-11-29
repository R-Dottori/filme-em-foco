
import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title='Filme em Foco',
    page_icon='🎥',
)

pag_1_title = 'Página Inicial'
pag_2_title = 'Exibir Filmes'
pag_3_title = 'Adicionar um Filme'


def pagina_um():
    st.title('Filme em Foco')
    st.image('https://daily.kellogg.edu/wp-content/uploads/2018/08/film-interpretation.jpg')


def pagina_dois():
    st.header(pag_2_title)
    filmes = ''
    genero = st.text_input('Buscar por gênero:')
    if genero:
        try:
            resp = requests.get(f'http://127.0.0.1:8000/filmes/genero/{genero}')
            filmes = resp.json()
        except:
            st.error('Erro na comunicação com a API.')
        if filmes != '':
            df_filmes = pd.DataFrame(filmes)
            st.write(df_filmes)

    else:
        try:
            resp = requests.get('http://127.0.0.1:8000/filmes')
            filmes = resp.json()
        except:
            st.error('Erro na comunicação com a API.')
        if filmes != '':
            df_filmes = pd.DataFrame(filmes)
            st.write(df_filmes)


def pagina_tres():
    st.header(pag_3_title)
    titulo = st.text_input('Título do Filme')
    ano = st.number_input('Ano de Lançamento')
    if st.button('Adicionar'):
        if ano and titulo:
            novo_filme = {
                            'titulo': titulo,
                            'titulo_original': titulo,
                            'ano': ano,
                            'duracao': 120,
                            'diretor': 'Diretor',
                            'roteirista': 'Roteirista',
                            'elenco': 'Ator',
                            'nota': 8.0,
                            'num_votos': 10.000,
                            'sinopse': 'Sinopse',
                            'genero': 'Ação',
                            'verba': 100,
                            'receita': 500
                            }
            try:
                resp = requests.post('http://127.0.0.1:8000/filmes', json=novo_filme)
                st.success('Filme adicionado com sucesso!')
            except:
                st.error('Erro ao comunicar com a API')
        else:
            st.error('Preencha todos os campos')


st.sidebar.title('Navegação')
pagina = st.sidebar.radio(label='Escolha uma página:', options=(pag_1_title, pag_2_title, pag_3_title))
if pagina == pag_1_title:
    pagina_um()
elif pagina == pag_2_title:
    pagina_dois()
else:
    pagina_tres()
