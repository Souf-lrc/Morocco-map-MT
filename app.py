import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium
from folium.features import GeoJsonPopup
from folium.plugins import Search, MeasureControl, Geocoder

# 1. CONFIGURATION (Doit impérativement être la 1ère commande Streamlit)
st.set_page_config(layout="wide", page_title="Réseau Électrique Maroc")

# 2. DÉFINITION DES FONCTIONS (On les définit d'abord)

def create_map():
    """Crée l'objet carte avec les paramètres de zoom fin [cite: 2]"""
    m = folium.Map(
        location=[33.8, -5.5],
        zoom_start=7,
        zoom_snap=0.1,
        zoom_delta=0.1,
        wheel_px_per_zoom_level=120,
        tiles=None,
        attr='© OpenStreetMap contributors'
    )
    # Fonds de carte [cite: 3, 4]
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='© Google Hybrid', name='Google Hybrid', overlay=False, control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='© Google Maps', name='Google Maps', overlay=False, control=True
    ).add_to(m)
    return m

@st.cache_data
def load_data():
    """Charge les données depuis le dossier data de GitHub [cite: 5]"""
    data_path = 'data/'
    zoning_path = data_path + 'Zoning solaire.xlsx'
    
    # Chargement des Excels [cite: 6, 7]
    zone1 = pd.read_excel(zoning_path, sheet_name='Zone1', decimal=',', engine='openpyxl')
    zone2 = pd.read_excel(zoning_path, sheet_name='Zone2', decimal=',', engine='openpyxl')
    zone3 = pd.read_excel(zoning_path, sheet_name='Zone3', decimal=',', engine='openpyxl')
    zone4_part1 = pd.read_excel(zoning_path, sheet_name='Zone4-part1', decimal=',', engine='openpyxl')
    zone4_part2 = pd.read_excel(zoning_path, sheet_name='Zone4-part2', decimal=',', engine='openpyxl')
    postes_df = pd.read_excel(zoning_path, sheet_name='Capacité_accueil_full', decimal=',', engine='openpyxl')

    # Chargement des Shapefiles [cite: 6]
    regions = gpd.read_file(data_path + 'regions/regions.shp')
    communes = gpd.read_file(data_path + '678ec1b952b09_Commune_Maroc/populaion_commune.shp').to_crs(epsg=4326)

    return zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df

def add_layers(m, regions, communes, postes_df):
    """Ajoute les couches géographiques et marqueurs [cite: 10, 13]"""
    # Régions
    folium.GeoJson(regions, style_function=lambda x: {'fillOpacity': 0, 'color': 'white', 'weight': 4}, name='Régions').add_to(m)

    # Communes avec recherche [cite: 11, 13]
    communes_layer = folium.FeatureGroup(name='Communes').add_to(m)
    folium.GeoJson(
        communes,
        style_function=lambda x: {'fillOpacity': 0, 'color': 'transparent', 'weight': 0},
        popup=folium.GeoJsonPopup(fields=['nom', 'Populati_1'], aliases=['Commune: ', 'Population: '])
    ).add_to(communes_layer)

    Search(layer=communes_layer, search_label='nom', placeholder='Rechercher une commune...').add_to(m)

    # Postes électriques [cite: 14, 15]
    for _, poste in postes_df.iterrows():
        if poste["Capacité d'accueil poste - 2027"] >= 2:
            # Logique bleu si 60kV, rouge sinon [cite: 15, 16]
            couleur = 'blue' if poste["Niveau de tension (kV)"] == 60 else 'red'
            
            folium.Marker(
                location=[poste['Latitude'], poste['Longitude']],
                popup=f"<b>{poste['Poste']}</b><br>Tension: {poste['Niveau de tension (kV)']} kV",
                icon=folium.Icon(color=couleur, icon='bolt', prefix='fa') [cite: 17]
            ).add_to(m)

    # Outils [cite: 23, 24]
    Geocoder().add_to(m)
    MeasureControl().add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

# 3. LOGIQUE PRINCIPALE (On appelle les fonctions ici)
st.title("⚡ Carte Interactive du Réseau")

try:
    # On charge les données [cite: 7]
    z1, z2, z3, z4p1, z4p2, regions, communes, postes_df = load_data()
    
    # On crée la carte
    ma_carte = create_map()
    
    # On ajoute les couches
    add_layers(ma_carte, regions, communes, postes_df)
    
    # Marqueur spécial
    folium.Marker(
        location=[35.10317622036963, -6.109536361502073],
        popup="Ferme Benjdya",
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(ma_carte)

    # Affichage final dans Streamlit
    st_folium(ma_carte, width="100%", height=700)

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
