
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
from bs4 import BeautifulSoup as bs
from wordcloud import WordCloud
import matplotlib.pyplot as plt


app_title = 'Subir e Baixar Arquivos'
pag_1_title = 'Carregar os Dados'
pag_2_title = 'Exibir Tabela'
pag_3_title = 'Mapa'
pag_4_title = 'Adicionar Complexos'
pag_5_title = 'Escolher um Filme'


@st.cache_data
def subir_base(arquivo):
    df = pd.read_csv(arquivo, index_col=0)
    return df


def pagina_um():
    if 'df' not in st.session_state:
        st.session_state['df'] = None

    if 'novo_df' not in st.session_state:
        st.session_state['novo_df'] = None
    
    st.title(app_title)
    st.header(pag_1_title)

    arquivo = st.file_uploader('Insira um arquivo CSV:', type='csv')
    if arquivo is not None:
        with st.spinner('Carregando...'):
            st.session_state['df'] = subir_base(arquivo)
            st.success('Base carregada com sucesso.')


def pagina_dois():
    st.header(pag_2_title)
    if st.session_state['df'] is not None:
        st.write(st.session_state['df'])
        if st.session_state['novo_df'] is not None:
            st.header('Baixar base com os novos dados:')
            df_download = st.session_state['df'].to_csv()
            st.download_button(
                label='Baixar',
                data=df_download,
                file_name='salas_rj_atualizado.csv'
                )
    else:
        st.warning('Aguardando o carregamento da base.')


def pagina_tres():
    st.header(pag_3_title)
    if st.session_state['df'] is not None:
        shapefile_rj = gpd.read_file('./data/Regioes Administrativas - RAs - PCRJ.zip')
        lat = -22.92
        lon = -43.47
        mapa_rj = folium.Map(location=[lat, lon], zoom_start=10)
        folium.GeoJson(shapefile_rj.to_json(), name='Regiões Administrativas',
                        style_function=lambda feature: {
                'fillColor': '#24b1f2',
                'color': 'black',
                'weight': 2,
                'dashArray': '5, 5',
                'fillOpacity': 0.5,
            }
        ).add_to(mapa_rj)

        for idx, sala in st.session_state['df'].iterrows():
            if idx <= 40:
                folium.Marker(
                    location=[sala['latitude'], sala['longitude']],
                    tooltip=sala['name'],
                    icon=folium.Icon(color='white')
                ).add_to(mapa_rj)
            else:
                folium.Marker(
                    location=[sala['latitude'], sala['longitude']],
                    tooltip=sala['name'],
                    icon=folium.Icon(icon='glyphicon glyphicon-film', color='red')
                ).add_to(mapa_rj)

        folium.LayerControl().add_to(mapa_rj)
        st_folium(mapa_rj)
    else:
        st.warning('Aguardando o carregamento da base.')


def pagina_quatro():
    st.header(pag_4_title)
    if st.session_state['df'] is not None:
        dados_exemplo = {'id': '1234', 'name': 'Nome do Complexo', 'neighborhood': 'Bairro', 'latitude': -22.92, 'longitude': -43.47}
        df_exemplo = pd.DataFrame(dados_exemplo, index=[0])
        st.write('Para adicionar novos dados, insira um arquivo CSV respeitando o seguinte esquema:')
        st.write(df_exemplo)

        novo_arquivo = st.file_uploader('Insira o arquivo CSV:', type='csv')
        if novo_arquivo is not None:
            with st.spinner('Carregando...'):
                st.session_state['novo_df'] = subir_base(novo_arquivo)
            if set(st.session_state['df'].columns) == set(st.session_state['novo_df'].columns):
                st.write(st.session_state['novo_df'])
                st.session_state['df'] = pd.concat([st.session_state['df'], st.session_state['novo_df']], ignore_index=True)
                st.success('Novos dados adicionados com sucesso.')
                st.header('Baixar base com os novos dados:')
                df_download = st.session_state['df'].to_csv()
                st.download_button(
                    label='Baixar',
                    data=df_download,
                    file_name='salas_rj_atualizado.csv'
                    )
            else:
                st.error('ERRO! Os dados inseridos não seguem o esquema exigido.')
    else:
        st.warning('Aguardando o carregamento da base.')


def pagina_cinco():
    st.header(pag_5_title)
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    raiz_api = 'https://api-content.ingresso.com/v0/Sessions/city/2/theater/{}'
    filme_escolhido = ''
    if st.session_state['df'] is not None:
        # Escolha do bairro e complexo de cinema
        st.header('Escolha um bairro e um cinema:')

        bairros = sorted(st.session_state['df']['neighborhood'].unique())
        filtro_bairro = st.selectbox(label='Selecione um bairro:', options=bairros)
        salas_bairro = st.session_state['df'][st.session_state['df']['neighborhood'] == filtro_bairro]['name'].unique()

        filtro_cinema = st.selectbox(label='Selecione um complexo de cinema:', options=salas_bairro)
        id_cinema = st.session_state['df'][st.session_state['df']['name'] == filtro_cinema]['id'].values[0]


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
            st.write(filmes_cartaz[['originalTitle']].drop_duplicates().sort_values('originalTitle'))
            filme_escolhido = st.selectbox(label='Selecione um filme:', options=sorted(filmes_cartaz['originalTitle'].drop_duplicates()))
        except:
            st.error('ERRO! Não encontramos sessões para o complexo escolhido. Por favor, selecione outro cinema.')

        # Após escolher um filme, faremos operações de raspagem no portal IMDb
        if filme_escolhido != '':
            st.header('IMDb')
            try:
                with st.spinner('Carregando...'):
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
            except:
                st.error('ERRO! Filme não encontrado no IMDb, por favor selecione outro.')
    else:
        st.warning('Aguardando o carregamento da base.')


st.sidebar.title('Navegação')
pagina = st.sidebar.radio(label='Escolha uma página:', options=(pag_1_title, pag_2_title, pag_3_title, pag_4_title, pag_5_title))
if pagina == pag_1_title:
    pagina_um()
elif pagina == pag_2_title:
    pagina_dois()
elif pagina == pag_3_title:
    pagina_tres()
elif pagina == pag_4_title:
    pagina_quatro()
else:
    pagina_cinco()
