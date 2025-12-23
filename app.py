import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium # Import important
from folium.plugins import Search, MeasureControl, Geocoder

# Configuration de la page Streamlit pour le mobile
st.set_page_config(layout="wide", page_title="Carte des Postes Électriques")

# Modification de la fonction de chargement (lecture locale)
@st.cache_data # Pour éviter de recharger les données à chaque clic
def load_data():
    data_path = 'data/' # Chemin vers votre dossier dans GitHub
    
    # Lecture des fichiers Excel (identique à votre code mais sans Drive)
    zoning_path = data_path + 'Zoning solaire.xlsx'
    # ... (vos lectures pd.read_excel ici) ...
    
    # Lecture des Shapefiles
    regions = gpd.read_file(data_path + 'regions/regions.shp')
    communes = gpd.read_file(data_path + '678ec1b952b09_Commune_Maroc/populaion_commune.shp').to_crs(epsg=4326)
    
    return zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df

# ... (Gardez vos fonctions create_map et add_layers telles quelles) ...

# Logique principale de l'app
st.title("⚡ Réseau Électrique - Visualisation")

# Chargement
zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df = load_data()

# Création et affichage
m = create_map()
m = add_layers(m, zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df)

# Affichage dans Streamlit (ajusté pour mobile)
st_folium(m, width="100%", height=700, returned_objects=[])
