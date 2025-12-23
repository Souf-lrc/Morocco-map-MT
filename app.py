import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MeasureControl, Geocoder

# 1. Configuration de la page et CSS pour Mobile
st.set_page_config(layout="wide", page_title="Carte Postes Électriques")

# Injection de CSS pour réduire la taille des polices et optimiser l'espace
st.markdown("""
    <style>
        /* Réduire les marges de l'application Streamlit pour gagner de la place */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
        
        /* Réduire la police du contrôleur de couches (Filtres) */
        .leaflet-control-layers {
            font-size: 10px !important;
            line-height: 12px !important;
        }
        .leaflet-control-layers label {
            margin-bottom: 2px !important;
        }
        
        /* Réduire la taille de la barre de recherche (Geocoder) */
        .leaflet-control-geocoder-icon {
            width: 26px !important;
            height: 26px !important;
        }
        .leaflet-control-geocoder-form input {
            font-size: 10px !important;
            padding: 4px !important;
        }
        
        /* Ajuster la taille des résultats de recherche */
        .leaflet-control-geocoder-alternatives {
            font-size: 10px !important;
            width: 200px !important;
        }
    </style>
""", unsafe_allow_html=True)

def create_map():
    """Initialise la carte avec les différents fonds."""
    m = folium.Map(
        location=[33.8, -5.5],
        zoom_start=7,
        zoom_snap=0.1,
        zoom_delta=0.1,
        wheel_px_per_zoom_level=120,
        tiles=None
    )

    # Fonds de carte
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='© Google Hybrid', name='Google Hybrid', overlay=False, control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='© Google Satellite', name='Google Satellite', overlay=False, control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='ESRI World Topo Map', name='ESRI Topo', overlay=False, control=True
    ).add_to(m)
    
    return m

@st.cache_data
def load_postes():
    """Charge les données des postes."""
    data_path = 'data/'
    zoning_path = data_path + 'Zoning solaire.xlsx'
    df = pd.read_excel(zoning_path, sheet_name='Capacité_accueil_full', decimal=',', engine='openpyxl')
    return df

# 2. Logique principale
# Titre plus petit pour gagner de la place sur mobile
st.markdown("### ⚡ Réseau Électrique")

try:
    postes_df = load_postes()
    m = create_map()

    # Groupes de couches
    postes_layer = folium.FeatureGroup(name='Postes électriques', show=True).add_to(m)
    cercles_layer = folium.FeatureGroup(name='Rayons 5km', show=False).add_to(m)

    for _, poste in postes_df.iterrows():
        if poste["Capacité d'accueil poste - 2027"] < 2:
            continue

        couleur = 'blue' if poste["Niveau de tension (kV)"] == 60 else 'red'

        # Popup HTML compact
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 11px; width: 150px;">
            <b>{poste['Poste']}</b>
            <hr style="margin: 3px 0;">
            Tens.: {poste['Niveau de tension (kV)']} kV<br>
            Cap.: {poste["Capacité d'accueil poste - 2027"]} MW
        </div>
        """

        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{poste['Poste']}",
            icon=folium.Icon(color=couleur, icon='bolt', prefix='fa')
        ).add_to(postes_layer)

        # Cercle de 5km (5000 mètres)
        folium.Circle(
            location=[poste['Latitude'], poste['Longitude']],
            radius=5000, 
            color=couleur,
            fill=True,
            fill_opacity=0.05,
            popup=f"Zone 5km - {poste['Poste']}"
        ).add_to(cercles_layer)

    # Marqueur Ferme Benjdya
    folium.Marker(
        location=[35.10317622036963, -6.109536361502073],
        popup="Ferme Benjdya",
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(m)

    # Outils
    Geocoder(position='topleft').add_to(m) # Déplacé à gauche pour équilibrer
    MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)
    
    # Filtres en bas à droite
    folium.LayerControl(collapsed=False, position='bottomright').add_to(m)

    # Affichage optimisé : Hauteur réduite à 75vh (75% de la hauteur de l'écran) ou 600px max
    # Cela permet de voir les boutons du bas sans scroller
    st_folium(m, width="100%", height=600, returned_objects=[])

except Exception as e:
    st.error(f"Erreur : {e}")
