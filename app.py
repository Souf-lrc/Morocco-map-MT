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


# Création de la carte
m = create_map()
zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df = load_data()

# Ajout des couches
def add_layers(m, zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df):
    # # Couche des zones solaires
    # for zone, color, label in [
    #     (zone1, 'red', 'Zone 1 - Potentiel solaire élevé'),
    #     (zone2, 'blue', 'Zone 2 - Potentiel solaire moyen'),
    #     (zone3, 'green', 'Zone 3 - Potentiel solaire moyen'),
    #     (zone4_part1, 'purple', 'Zone 4 - Potentiel solaire moyen'),
    #     (zone4_part2, 'purple', 'Zone 4 - Potentiel solaire moyen')
    # ]:
    #     folium.Polygon(
    #         locations=zone[['Latitude', 'Longitude']].values.tolist(),
    #         color=color,
    #         fill=True,
    #         # fill_opacity=0.03,
    #         fill_opacity=0.0,
    #         popup=label
    #     ).add_to(m)

    # Couche des régions
    regions_layer = folium.FeatureGroup(name='Régions', show=True).add_to(m)
    folium.GeoJson(
        regions,
        style_function=lambda x: {'fillOpacity': 0, 'color': 'white', 'weight': 4}
    ).add_to(regions_layer)

    # Couche des communes
    communes_layer = folium.FeatureGroup(name='Communes', show=True).add_to(m)
    geojson_communes = folium.GeoJson(
        communes,
        style_function=lambda x: {
            'fillOpacity': 0,
            'color': 'transparent',
            'weight': 0
        },
        popup=folium.GeoJsonPopup(
            fields=['nom', 'Populati_1'],
            aliases=['Commune: ', 'Population: '],
            localize=True,
            style="background-color: white; z-index: 1000; font-weight: bold;"
        ),
        highlight_function=lambda x: {
            'color': 'blue',
            'weight': 2,
            'fillOpacity': 0.2,
            'fillColor': 'lightblue'
        }
    ).add_to(communes_layer)

    # Ajout de la fonctionnalité de recherche pour les communes
    Search(
        layer=communes_layer,
        search_label='nom',
        placeholder='Rechercher une commune...',
        collapsed=False,
        position='topleft'
    ).add_to(m)

    # Couche des postes électriques avec labels permanents
    postes_layer = folium.FeatureGroup(name='Postes électriques', show=True).add_to(m)

    # Nouvelle couche pour les cercles
    cercles_layer = folium.FeatureGroup(name='Rayons 20km', show=False).add_to(m)

    # Couleurs basées sur le GRD (vous devrez ajuster selon vos données)
    # Supposons qu'il y a une colonne 'GRD' dans votre DataFrame
    # # Si elle n'existe pas, vous devrez l'ajouter ou utiliser une autre logique
    # grd_colors = {
    #     'ONEE': 'blue',
    #     'RADEM': 'red'
    # }

    for idx, poste in postes_df.iterrows():
        capacite = poste["Capacité d'accueil poste - 2027"]
        if capacite < 2:
            continue  # Passer au poste suivant si capacité <= seuil

        # Déterminer la couleur basée sur le GRD
        # Si vous n'avez pas de colonne GRD, vous pouvez utiliser une logique basée sur le nom ou la région
        if poste["Niveau de tension (kV)"] == 60:
          couleur = 'blue'
        else:
          couleur = 'red'

        # Ajouter marqueur principal
        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            popup=f"""
            <div style="font-size: 12px;">
                <b>{poste['Poste']}</b><br>
                Tension: {poste['Niveau de tension (kV)']} kV<br>
                Capacité 2027: {poste["Capacité d'accueil poste - 2027"]} MW
            </div>
            """,
            tooltip=f"{poste['Poste']}",
            icon=folium.Icon(color=couleur, icon='bolt', prefix='fa')
        ).add_to(postes_layer)

        # Ajouter un label permanent avec informations sur plusieurs lignes
        folium.Marker(
            location=[poste['Latitude'], poste['Longitude']],
            icon=folium.DivIcon(
                html=f'''
                <div style="
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 1px solid black;
                    padding: 4px;
                    font-size: 10px;
                    border-radius: 3px;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    white-space: nowrap;
                ">
                    <b>{poste['Poste']}</b><br>
                    Tension: {poste['Niveau de tension (kV)']} kV<br>
                    Capacité 2027: {poste["Capacité d'accueil poste - 2027"]} MW
                </div>
                ''',
                icon_size=(140, 50),  # Taille légèrement augmentée pour accommoder le texte plus long
                icon_anchor=(70, -10)  # Ajusté pour rester centré
            )
        ).add_to(postes_layer)

        # Ajouter cercle (masqué par défaut)
        folium.Circle(
            location=[poste['Latitude'], poste['Longitude']],
            radius=15000,
            color=couleur,
            fill=True,
            fill_opacity=0.05,
            popup=f"Rayon 20km - {poste['Poste']}"
        ).add_to(cercles_layer)

    # Ajout du géocodage avec un fournisseur alternatif (OpenStreetMap)
    Geocoder(
        position='topright',
        collapsed=True,
        add_marker=True,
        provider='nominatim',  # Utilisation de Nominatim (OpenStreetMap)
        search_label='display_name',
        placeholder='Rechercher un lieu...',
        zoom=12
    ).add_to(m)

    # Ajout de l'outil de mesure
    measure_control = MeasureControl(
        position='bottomleft',
        primary_length_unit='kilometers',
        secondary_length_unit='meters',
        primary_area_unit='hectares',
        secondary_area_unit='sqmeters'
    )
    m.add_child(measure_control)

    return m



# Coordonnées du point spécifique
special_lat, special_lon = 35.10317622036963, -6.109536361502073

# Ajout du marqueur distinctif
folium.Marker(
    location=[special_lat, special_lon],
    popup="Ferme Benjdya",
    tooltip="Cliquez pour plus d'infos",
    icon=folium.Icon(color='orange', icon='star', prefix='fa') # 'fa' pour FontAwesome
).add_to(m)


# Logique principale de l'app
st.title("⚡ Réseau Électrique - Visualisation")

# Chargement
zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df = load_data()

# Création et affichage
m = create_map()
m = add_layers(m, zone1, zone2, zone3, zone4_part1, zone4_part2, regions, communes, postes_df)

# Affichage dans Streamlit (ajusté pour mobile)
st_folium(m, width="100%", height=700, returned_objects=[])
