import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium
from folium.plugins import Search, MeasureControl, Geocoder

# 1. Configuration initiale
st.set_page_config(layout="wide", page_title="Carte Énergétique Maroc")

def create_map():
    # Paramètres de zoom fin [cite: 2]
    m = folium.Map(
        location=[33.8, -5.5],
        zoom_start=12,
        zoom_snap=0.1,
        zoom_delta=0.1,
        wheel_px_per_zoom_level=120,
        tiles=None,
        attr='© OpenStreetMap contributors'
    )

    # Ajout des fonds de carte [cite: 3, 4]
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='© Google Hybrid', name='Google Hybrid', overlay=False, control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='© Google Maps', name='Google Maps', overlay=False, control=True
    ).add_to(m)

    return m

# @st.cache_data
# def load_data():
#     # Accès aux fichiers dans le dossier /data du dépôt GitHub [cite: 5]
#     data_path = 'data/'
#     zoning_path = data_path + 'Zoning solaire.xlsx'

#     # Chargement des zones et postes [cite: 5, 7]
#     zone1 = pd.read_excel(zoning_path, sheet_name='Zone1', decimal=',', engine='openpyxl')
#     zone2 = pd.read_excel(zoning_path, sheet_name='Zone2', decimal=',', engine='openpyxl')
#     zone3 = pd.read_excel(zoning_path, sheet_name='Zone3', decimal=',', engine='openpyxl')
#     zone4_part1 = pd.read_excel(zoning_path, sheet_name='Zone4-part1', decimal=',', engine='openpyxl')
#     zone4_part2 = pd.read_excel(zoning_path, sheet_name='Zone4-part2', decimal=',', engine='openpyxl')
#     postes_df = pd.read_excel(zoning_path, sheet_name='Capacité_accueil_full', decimal=',', engine='openpyxl')

#     # Chargement et simplification des régions
#     regions = gpd.read_file(data_path + 'regions/regions.shp')
#     regions = regions.simplify(0.01, preserve_topology=True) # Allège le tracé [cite: 10]
    
#     # Chargement et simplification des communes
#     communes = gpd.read_file(data_path + '678ec1b952b09_Commune_Maroc/populaion_commune.shp').to_crs(epsg=4326)
#     communes.geometry = communes.geometry.simplify(0.001, preserve_topology=True) # Allège les communes 

#     return zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df

# def add_layers(m, regions, communes, postes_df):
#     # Couche des régions [cite: 10]
#     folium.GeoJson(
#         regions,
#         style_function=lambda x: {'fillOpacity': 0, 'color': 'white', 'weight': 4},
#         name='Régions'
#     ).add_to(m)

#     # Couche des communes avec popup [cite: 11, 12]
#     communes_layer = folium.FeatureGroup(name='Communes').add_to(m)
#     folium.GeoJson(
#         communes,
#         style_function=lambda x: {'fillOpacity': 0, 'color': 'transparent', 'weight': 0},
#         popup=folium.GeoJsonPopup(
#             fields=['nom', 'Populati_1'],
#             aliases=['Commune: ', 'Population: '],
#             style="background-color: white; font-weight: bold;"
#         ),
#         highlight_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0.2}
#     ).add_to(communes_layer)

#     # Recherche [cite: 13]
#     Search(layer=communes_layer, search_label='nom', placeholder='Chercher commune...').add_to(m)

#     # Postes électriques [cite: 14, 15]
#     postes_layer = folium.FeatureGroup(name='Postes électriques').add_to(m)
#     cercles_layer = folium.FeatureGroup(name='Rayons 15km', show=False).add_to(m)

#     # for _, poste in postes_df.iterrows():
#     #     if poste["Capacité d'accueil poste - 2027"] < 2:
#     #         continue

#     #     # Logique de couleur selon tension 
#     #     couleur = 'blue' if poste["Niveau de tension (kV)"] == 60 else 'red'

#     #     # Marqueur principal [cite: 17]
#     #     folium.Marker(
#     #         location=[poste['Latitude'], poste['Longitude']],
#     #         popup=f"<b>{poste['Poste']}</b><br>Tension: {poste['Niveau de tension (kV)']} kV",
#     #         icon=folium.Icon(color=couleur, icon='bolt', prefix='fa')
#     #     ).add_to(postes_layer)

#     #     # Label permanent [cite: 18, 19, 20, 21]
#     #     folium.Marker(
#     #         location=[poste['Latitude'], poste['Longitude']],
#     #         icon=folium.DivIcon(
#     #             html=f'<div style="background: white; border: 1px solid black; padding: 2px; font-size: 9px;">{poste["Poste"]}</div>',
#     #             icon_anchor=(0, 0)
#     #         )
#     #     ).add_to(postes_layer)

#     #     # Cercle de rayon 15km [cite: 22]
#     #     folium.Circle(
#     #         location=[poste['Latitude'], poste['Longitude']],
#     #         radius=15000, color=couleur, fill=True, fill_opacity=0.05
#     #     ).add_to(cercles_layer)

#     # # Outils [cite: 23, 24]
#     # Geocoder(position='topright').add_to(m)
#     # MeasureControl(primary_length_unit='kilometers', primary_area_unit='hectares').add_to(m)
#     # folium.LayerControl(collapsed=False).add_to(m)

# 3. Lancement de l'application
st.title("⚡ Réseau Électrique Maroc")

try:
    # z1, z2, z3, z4p1, z4p2, regions, communes, postes_df = load_data()
    m = create_map()
    # add_layers(m, regions, communes, postes_df)
    
    # Marqueur spécial
    folium.Marker(
        location=[35.10317622036963, -6.109536361502073],
        popup="Ferme Benjdya",
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(m)

    st_folium(m, width="100%", height=700)
except Exception as e:
    st.error(f"Erreur : {e}")
