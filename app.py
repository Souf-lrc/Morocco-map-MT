import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium
from folium.features import GeoJsonPopup
from folium.plugins import Search, MeasureControl, Geocoder

# 1. Configuration de la page (Doit être la première commande Streamlit)
st.set_page_config(layout="wide", page_title="Carte Réseau Électrique Maroc")

# 2. Fonctions de configuration de la carte
def create_map():
    """Initialise la carte avec les réglages de zoom fin et les fonds de carte."""
    m = folium.Map(
        location=[33.8, -5.5],
        zoom_start=7,
        zoom_snap=0.1,
        zoom_delta=0.1,
        wheel_px_per_zoom_level=120,
        tiles=None,
        attr='© OpenStreetMap contributors'
    )

    # Ajout des fonds de carte
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='© Google Hybrid',
        name='Google Hybrid',
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='© Google Maps',
        name='Google Maps (Normal)',
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='© Google Satellite',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='ESRI World Topo Map',
        name='ESRI Topo',
        overlay=False,
        control=True
    ).add_to(m)

    return m

@st.cache_data
def load_data():
    """Charge les données depuis le dossier local 'data/'."""
    data_path = 'data/'
    zoning_path = data_path + 'Zoning solaire.xlsx'

    # [cite_start]Lecture des zones solaires [cite: 5]
    zone1 = pd.read_excel(zoning_path, sheet_name='Zone1', decimal=',', engine='openpyxl')
    zone2 = pd.read_excel(zoning_path, sheet_name='Zone2', decimal=',', engine='openpyxl')
    zone3 = pd.read_excel(zoning_path, sheet_name='Zone3', decimal=',', engine='openpyxl')
    zone4_part1 = pd.read_excel(zoning_path, sheet_name='Zone4-part1', decimal=',', engine='openpyxl')
    zone4_part2 = pd.read_excel(zoning_path, sheet_name='Zone4-part2', decimal=',', engine='openpyxl')

    # [cite_start]Régions et Communes (Shapefiles) [cite: 5, 6]
    regions = gpd.read_file(data_path + 'regions/regions.shp')
    # [cite_start]Attention à l'orthographe du fichier 'populaion' [cite: 6]
    communes = gpd.read_file(data_path + '678ec1b952b09_Commune_Maroc/populaion_commune.shp').to_crs(epsg=4326)

    # [cite_start]Postes électriques [cite: 7]
    postes_df = pd.read_excel(zoning_path, sheet_name='Capacité_accueil_full', decimal=',', engine='openpyxl')

    return zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df

def add_layers(m, zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df):
    """Ajoute toutes les couches de données à la carte."""
    
    # [cite_start]1. Couche des régions [cite: 10]
    regions_layer = folium.FeatureGroup(name='Régions', show=True).add_to(m)
    folium.GeoJson(
        regions,
        style_function=lambda x: {'fillOpacity': 0, 'color': 'white', 'weight': 4}
    ).add_to(regions_layer)

    # [cite_start]2. Couche des communes [cite: 11]
    communes_layer = folium.FeatureGroup(name='Communes', show=True).add_to(m)
    folium.GeoJson(
        communes,
        style_function=lambda x: {'fillOpacity': 0, 'color': 'transparent', 'weight': 0},
        popup=folium.GeoJsonPopup(
            fields=['nom', 'Populati_1'],
            aliases=['Commune: ', 'Population: '],
            localize=True,
            style="background-color: white; z-index: 1000; font-weight: bold;"
        ),
        highlight_function=lambda x: {
            'color': 'blue', 'weight': 2, 'fillOpacity': 0.2, 'fillColor': 'lightblue'
        }
    ).add_to(communes_layer)

    # [cite_start]3. Barre de recherche [cite: 13]
    Search(
        layer=communes_layer,
        search_label='nom',
        placeholder='Rechercher une commune...',
        collapsed=False,
        position='topleft'
    ).add_to(m)

    # [cite_start]4. Couche des postes électriques [cite: 14]
    postes_layer = folium.FeatureGroup(name='Postes électriques', show=True).add_to(m)
    cercles_layer = folium.FeatureGroup(name='Rayons 15km', show=False).add_to(m)

    for idx, poste in postes_df.iterrows():
        capacite = poste["Capacité d'accueil poste - 2027"]
        [cite_start]if capacite < 2: [cite: 15]
            continue

        # [cite_start]Logique de couleur : Bleu pour 60kV, Rouge pour le reste [cite: 15, 16]
        couleur = 'blue' if poste["Niveau de tension (kV)"] == 60 else 'red'

        # [cite_start]Marqueur avec icône [cite: 17]
        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            popup=f"<b>{poste['Poste']}</b><br>Tension: {poste['Niveau de tension (kV)']} kV<br>Capacité 2027: {poste['Capacité d\'accueil poste - 2027']} MW",
            tooltip=f"{poste['Poste']}",
            icon=folium.Icon(color=couleur, icon='bolt', prefix='fa')
        ).add_to(postes_layer)

        # [cite_start]Label permanent (DivIcon) [cite: 18, 19, 20, 21]
        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            icon=folium.DivIcon(
                html=f'''
                <div style="background-color: rgba(255, 255, 255, 0.9); border: 1px solid black; padding: 4px; 
                font-size: 10px; border-radius: 3px; text-align: center; white-space: nowrap;">
                    <b>{poste['Poste']}</b><br>{poste['Niveau de tension (kV)']} kV | {poste['Capacité d\'accueil poste - 2027']} MW
                </div>
                ''',
                icon_size=(140, 50),
                icon_anchor=(70, -10)
            )
        ).add_to(postes_layer)

        # [cite_start]Cercle de rayon [cite: 22]
        folium.Circle(
            location=[poste['Latitude'], poste['Longitude']],
            radius=15000,
            color=couleur,
            fill=True,
            fill_opacity=0.05
        ).add_to(cercles_layer)

    # [cite_start]5. Outils supplémentaires [cite: 23, 24]
    Geocoder(position='topright', provider='nominatim', zoom=12).add_to(m)
    MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    return m

# 3. Exécution principale de l'application
st.title("⚡ Carte du Réseau Électrique et Potentiel Solaire")

# Chargement des données
try:
    data = load_data()
    zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df = data

    # Création de la carte
    m = create_map()
    m = add_layers(m, zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df)

    # [cite_start]Ajout du marqueur spécial (Ferme Benjdya) [cite: 24]
    folium.Marker(
        location=[35.10317622036963, -6.109536361502073],
        popup="Ferme Benjdya",
        tooltip="Point d'intérêt spécial",
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(m)

    # Affichage dans Streamlit
    st_folium(m, width="100%", height=700, returned_objects=[])

except Exception as e:
    st.error(f"Erreur lors du chargement des données ou de la carte : {e}")
    st.info("Vérifiez que vos fichiers sont bien dans le dossier 'data/' sur votre dépôt GitHub.")
