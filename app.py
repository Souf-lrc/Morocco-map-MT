import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MeasureControl, Geocoder

# 1. Configuration de la page
st.set_page_config(layout="wide", page_title="Carte Postes Électriques")

# CSS pour l'application Streamlit (Marges externes)
st.markdown("""
    <style>
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

def create_map():
    """Initialise la carte."""
    m = folium.Map(
        location=[33.8, -5.5],
        zoom_start=7,
        zoom_snap=0.1,
        zoom_delta=0.1,
        tiles=None
    )

    # --- INJECTION DU CSS DANS LA CARTE ---
    map_custom_css = """
    <style>
        /* Réduire la police du panneau de filtres */
        .leaflet-control-layers {
            font-size: 10px !important;
            line-height: 12px !important;
            padding: 5px !important;
        }
        /* Réduire l'espacement entre les options */
        .leaflet-control-layers label {
            margin-bottom: 0px !important;
            display: flex !important;
            align-items: center !important;
        }
        /* Réduire la taille des checkbox */
        .leaflet-control-layers input[type="radio"], 
        .leaflet-control-layers input[type="checkbox"] {
            margin: 2px 5px 2px 0 !important;
            height: 12px !important;
            width: 12px !important;
        }
        /* Réduire la barre de recherche */
        .leaflet-control-geocoder-icon {
            width: 24px !important;
            height: 24px !important;
        }
        .leaflet-control-geocoder-form input {
            font-size: 11px !important;
            padding: 3px !important;
            height: 24px !important;
        }
    </style>
    """
    m.get_root().html.add_child(folium.Element(map_custom_css))

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
    """Charge les données."""
    data_path = 'data/'
    zoning_path = data_path + 'Zoning solaire.xlsx'
    df = pd.read_excel(zoning_path, sheet_name='Capacité_accueil_full', decimal=',', engine='openpyxl')
    return df

# 2. Logique principale
st.markdown("<h4 style='margin: 0px; padding-bottom: 5px;'>⚡ Cartopgraphie des postes électriques </h4>", unsafe_allow_html=True)

try:
    postes_df = load_postes()
    m = create_map()

    # Couches
    postes_layer = folium.FeatureGroup(name='Postes', show=True).add_to(m)
    cercles_layer = folium.FeatureGroup(name='Rayons 5km', show=False).add_to(m)

    for _, poste in postes_df.iterrows():
        if poste["Capacité d'accueil poste - 2027"] < 2:
            continue

        couleur = 'blue' if poste["Niveau de tension (kV)"] == 60 else 'red'

        # Popup HTML
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 11px; width: 140px;">
            <b>{poste['Poste']}</b>
            <hr style="margin: 3px 0;">
            {poste['Niveau de tension (kV)']} kV | Capacité 2027: {poste["Capacité d'accueil poste - 2027"]} MW
        </div>
        """

        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{poste['Poste']}",
            icon=folium.Icon(color=couleur, icon='bolt', prefix='fa')
        ).add_to(postes_layer)

        # Cercle 5km
        folium.Circle(
            location=[poste['Latitude'], poste['Longitude']],
            radius=5000, 
            color=couleur,
            fill=True, fill_opacity=0.05,
            popup=f"Zone 5km - {poste['Poste']}"
        ).add_to(cercles_layer)

    # Point spécifique
    folium.Marker(
        location=[35.10317622036963, -6.109536361502073],
        popup="Ferme Benjdya",
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(m)

    # Outils
    # CHANGEMENT ICI : position='topright'
    Geocoder(position='topright').add_to(m)
    
    MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)
    
    # Filtres
    folium.LayerControl(collapsed=False, position='bottomright').add_to(m)

    # Affichage optimisé mobile
    st_folium(m, width="100%", height=600, returned_objects=[])

except Exception as e:
    st.error(f"Erreur : {e}")
