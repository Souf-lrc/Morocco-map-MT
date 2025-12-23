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
    # Chemin relatif vers votre dossier 'data' sur GitHub
    data_path = 'data/' 

    # 1. Chargement du fichier Excel
    zoning_path = data_path + 'Zoning solaire.xlsx'
    
    # Il est CRUCIAL que ces lignes d'assignation existent avant le 'return'
    zone1 = pd.read_excel(zoning_path, sheet_name='Zone1', decimal=',', engine='openpyxl')
    zone2 = pd.read_excel(zoning_path, sheet_name='Zone2', decimal=',', engine='openpyxl')
    zone3 = pd.read_excel(zoning_path, sheet_name='Zone3', decimal=',', engine='openpyxl')
    zone4_part1 = pd.read_excel(zoning_path, sheet_name='Zone4-part1', decimal=',', engine='openpyxl')
    zone4_part2 = pd.read_excel(zoning_path, sheet_name='Zone4-part2', decimal=',', engine='openpyxl')

    # 2. Chargement des Shapefiles
    regions = gpd.read_file(data_path + 'regions/regions.shp')
    # Vérifiez bien le nom du dossier pour les communes dans votre GitHub
    communes = gpd.read_file(data_path + '678ec1b952b09_Commune_Maroc/populaion_commune.shp').to_crs(epsg=4326)

    # 3. Postes électriques
    postes_df = pd.read_excel(zoning_path, sheet_name='Capacité_accueil_full', decimal=',', engine='openpyxl')

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
