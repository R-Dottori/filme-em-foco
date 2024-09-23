
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title('Interface de Usuário')

st.header('Complexos de Cinema no Rio de Janeiro')
salas_rj = pd.read_csv('./data/salas_rj.csv', index_col=0)
# salas_filtradas = salas_rj[['name', 'neighborhood']].sort_values('neighborhood').reset_index(drop=True)
bairros = sorted(salas_rj['neighborhood'].unique())
filtro = st.multiselect(label='Selecione quais bairros deseja exibir:', options=bairros, default=bairros)
st.write(salas_rj[['name', 'neighborhood']][salas_rj['neighborhood'].isin(filtro)].sort_values('neighborhood'))

st.header('Mapa dos Complexos por Região Administrativa')
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

for idx, sala in salas_rj.iterrows():
    folium.Marker(
        location=[sala['latitude'], sala['longitude']],
        tooltip=sala['name'],
        icon=folium.Icon(color='white')
    ).add_to(mapa_rj)

folium.LayerControl().add_to(mapa_rj)
st_folium(mapa_rj)
