
import streamlit as st
import pandas as pd

pag_1_title = 'Página 1 - Carregando os Dados'
pag_2_title = 'Página 2 - Exibindo os Dados'


@st.cache_data
def subir_base(arquivo):
    df = pd.read_csv(arquivo, index_col=0)
    return df


def pagina_um():
    if 'df' not in st.session_state:
        st.session_state['df'] = None
    
    st.title('Cache e Estado de Sessão')
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
    else:
        st.warning('Aguardando o carregamento da base.')


st.sidebar.title('Navegação')
pagina = st.sidebar.radio(label='Escolha uma página:', options=(pag_1_title, pag_2_title))
if pagina == pag_1_title:
    pagina_um()
else:
    pagina_dois()
