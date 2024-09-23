import streamlit as st
import pandas as pd

salas_ancine = pd.read_csv('./data/salas_rj_ancine.csv')
salas_api = pd.read_csv('./data/salas_rj_api.csv')

st.title('Filme em Foco')

st.header('Sobre:')
st.write("""O objetivo do aplicativo é exibir de maneira intuitiva e interativa dados
        sobre a distribuição de complexos de cinema no município do Rio de Janeiro e
        a bilheteria de cada produção, destacando obras nacionais.""")
st.write("""Espero que esse relatório possa ser utilizado para promover um acesso à cultura
        e ao cinema mais igualitário, além de incentivar o consumo de obras brasileiras.""")

st.header('Dados Utilizados:')
st.subheader('Salas de Cinema no Rio de Janeiro (Dados da ANCINE):')
st.write(salas_ancine)

st.subheader('Salas de Cinema no Rio de Janeiro (Dados da API do Ingresso.com):')
st.write(salas_api)

st.header('Fontes e Inspirações:')
st.write('https://www.who.int/europe/publications/i/item/9789289054553')
st.write('https://www.gov.br/ancine/pt-br/oca/dados-abertos')
st.write('https://suporte.ingresso.com/portal/pt-br/kb/articles/integra%C3%A7%C3%A3o-com-a-api-de-conte%C3%BAdo-1-11-2022')
