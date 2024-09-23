
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

app_title = 'Subir e Baixar Arquivos'
pag_1_title = 'Carregar os Dados'
pag_2_title = 'Exibir Tabela'
pag_3_title = 'Mapa'
pag_4_title = 'Adicionar Complexos'


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


st.sidebar.title('Navegação')
pagina = st.sidebar.radio(label='Escolha uma página:', options=(pag_1_title, pag_2_title, pag_3_title, pag_4_title))
if pagina == pag_1_title:
    pagina_um()
elif pagina == pag_2_title:
    pagina_dois()
elif pagina == pag_3_title:
    pagina_tres()
else:
    pagina_quatro()
