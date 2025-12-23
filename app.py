import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MeasureControl, Geocoder

# 1. Configuration de la page
st.set_page_config(layout="wide", page_title="Carte Postes Électriques")

def create_map():
    """Initialise la carte avec zoom fluide et fond Google Hybrid."""
    m = folium.Map(
        location=[33.8, -5.5],
        zoom_start=7,
        zoom_snap=0.1,
        zoom_delta=0.1,
        wheel_px_per_zoom_level=120,
        tiles=None
    )

    # Ajout du fond Google Hybrid uniquement pour la performance
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='© Google Hybrid',
        name='Google Hybrid',
        overlay=False,
        control=True
    ).add_to(m)
    
    return m

@st.cache_data
def load_postes():
    """Charge uniquement les données des postes électriques."""
    data_path = 'data/'
    zoning_path = data_path + 'Zoning solaire.xlsx'
    
    # Lecture de la feuille spécifique aux postes 
    df = pd.read_excel(
        zoning_path, 
        sheet_name='Capacité_accueil_full', 
        decimal=',', 
        engine='openpyxl'
    )
    return df

# 2. Logique principale
st.title("⚡ Localisation des Postes Électriques")

try:
    postes_df = load_postes()
    m = create_map()

    # Ajout des postes électriques
    for _, poste in postes_df.iterrows():
        # Filtre de capacité [cite: 15]
        if poste["Capacité d'accueil poste - 2027"] < 2:
            continue

        # Logique de couleur : Bleu pour 60kV, Rouge pour les autres [cite: 15, 16]
        couleur = 'blue' if poste["Niveau de tension (kV)"] == 60 else 'red'

        # Marqueur avec icône bolt [cite: 17]
        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            popup=f"<b>{poste['Poste']}</b><br>Tension: {poste['Niveau de tension (kV)']} kV",
            tooltip=poste['Poste'],
            icon=folium.Icon(color=couleur, icon='bolt', prefix='fa')
        ).add_to(m)

        # Label permanent simplifié [cite: 18, 19]
        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            icon=folium.DivIcon(
                html=f'<div style="background: white; border: 1px solid black; padding: 2px; font-size: 9px; border-radius:3px;">{poste["Poste"]}</div>',
                icon_anchor=(70, -10)
            )
        ).add_to(m)

    # Ajout du marqueur spécial [cite: 24]
    folium.Marker(
        location=[35.10317622036963, -6.109536361502073],
        popup="Ferme Benjdya",
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(m)

    # Outils utilitaires [cite: 23, 24]
    Geocoder(position='topright').add_to(m)
    MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)

    # Affichage de la carte
    # returned_objects=[] permet d'éviter les rechargements inutiles lors du clic
    st_folium(m, width="100%", height=700, returned_objects=[])

except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.info("Assurez-vous que 'data/Zoning solaire.xlsx' est présent sur GitHub.")
