import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MeasureControl, Geocoder

# 1. Configuration de la page
st.set_page_config(layout="wide", page_title="Carte Postes Électriques")

def create_map():
    """Initialise la carte avec les différents fonds de carte demandés."""
    m = folium.Map(
        location=[33.8, -5.5],
        zoom_start=7,
        zoom_snap=0.1,
        zoom_delta=0.1,
        wheel_px_per_zoom_level=120,
        tiles=None # On désactive le fond par défaut pour utiliser les nôtres
    )

    # Fond Google Hybrid
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='© Google Hybrid',
        name='Google Hybrid',
        overlay=False,
        control=True
    ).add_to(m)

    # Fond Google Satellite
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='© Google Satellite',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    # Fond ESRI Topo
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='ESRI World Topo Map',
        name='ESRI Topo',
        overlay=False,
        control=True
    ).add_to(m)
    
    return m

@st.cache_data
def load_postes():
    """Charge les données des postes électriques."""
    data_path = 'data/'
    zoning_path = data_path + 'Zoning solaire.xlsx'
    df = pd.read_excel(zoning_path, sheet_name='Capacité_accueil_full', decimal=',', engine='openpyxl')
    return df

# 2. Logique principale
st.title("⚡ Réseau Électrique - Consultation Mobile")

try:
    postes_df = load_postes()
    m = create_map()

    # Création des groupes de couches (Layer Groups)
    postes_layer = folium.FeatureGroup(name='Postes électriques', show=True).add_to(m)
    cercles_layer = folium.FeatureGroup(name='Rayons 20km', show=False).add_to(m)

    for _, poste in postes_df.iterrows():
        if poste["Capacité d'accueil poste - 2027"] < 2:
            continue

        # Logique de couleur : Bleu pour 60kV, Rouge pour le reste
        couleur = 'blue' if poste["Niveau de tension (kV)"] == 60 else 'red'

        # Préparation du contenu du Popup en HTML
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 13px; width: 200px;">
            <h4 style="margin-bottom: 5px;">{poste['Poste']}</h4>
            <hr style="margin: 5px 0;">
            <b>Tension :</b> {poste['Niveau de tension (kV)']} kV<br>
            <b>Capacité 2027 :</b> {poste["Capacité d'accueil poste - 2027"]} MW
        </div>
        """

        # Ajouter le marqueur avec le style demandé
        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{poste['Poste']} ({poste['Niveau de tension (kV)']} kV)",
            icon=folium.Icon(color=couleur, icon='bolt', prefix='fa')
        ).add_to(postes_layer)

        # Ajouter le cercle de 20km (masqué par défaut via le groupe)
        folium.Circle(
            location=[poste['Latitude'], poste['Longitude']],
            radius=20000,
            color=couleur,
            fill=True,
            fill_opacity=0.05,
            popup=f"Rayon 20km - {poste['Poste']}"
        ).add_to(cercles_layer)

    # Marqueur spécial (Ferme Benjdya)
    folium.Marker(
        location=[35.10317622036963, -6.109536361502073],
        popup="Ferme Benjdya",
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(m)

    # Contrôles de la carte
    Geocoder(position='topright').add_to(m)
    MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)
    
    # Ajout du sélecteur de couches (filtres)
    folium.LayerControl(collapsed=False, position='bottomright').add_to(m)

    # Affichage final
    st_folium(m, width="100%", height=700, returned_objects=[])

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
