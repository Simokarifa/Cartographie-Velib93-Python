# 1-Les Imports
import requests
from datetime import datetime, date
import folium
import json
from shapely.geometry import shape, Point
import folium.plugins
from config import configparser

# Liste des données à recupérer en bas dans le script
#url=configparser["DEFAULT"]["url_VelibData"]
url = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json"
urlStatus = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json"
cheminDep = './departement.geojson'
position = [48.853, 2.35]
zoom = 10
fond = r'https://tile.osm.ch/switzerland/{z}/{x}/{y}.png'


# 2-Fonctions Auxiliaires
# Fonction de recuperation des données
def recupData(url):
    answ = requests.get(url)
    # Verification du statut de la requette et conversion de la reponse en json
    if answ.status_code != 200:
        print("erreur dans la récupération des données")
    else:
        data = answ.json()
    # récupérer dans une liste, de l'ensemble des stations avec leurs coordonées et infos.
    donnees = data["data"]["stations"]
    return donnees


# Fonction de fusion des listes
def mergeData(data1, data2):
    dataFinale = []
    for i in data1:
        for j in data2:
            if i['station_id'] == j['station_id']:
                List = {}
                List['station_id'] = i['station_id']
                List['name'] = i['name']
                List['lat'] = i['lat']
                List['lon'] = i['lon']
                List['capacity'] = i['capacity']
                List['num_bikes_available'] = j['num_bikes_available']
                List['mechanical'] = j['num_bikes_available_types'][0]['mechanical']
                List['ebike'] = j['num_bikes_available_types'][1]['ebike']
                List['last_reported'] = j['last_reported']
                dataFinale.append(List)
                break
    return dataFinale


# Deuxieme methodes pour la fusion des listes en dictionnaire exploitable
#NB: j'ai utlisé la première methode
def mergeData2(liste1, liste2):
    # Transformation en dictionnaire
    dict1,dict2 = {x['station_id']: x for x in liste1},{x['station_id']: x for x in liste2}
    # fusion des données
    donnees = {k: {**v, **dict1[k]} for k, v in dict2.items()}
    return donnees


# Fonction d'affichage de la popup sur la carte
def mapopup(a, b, c, d, e, f, g):
    """
    Fonction qui rempli un template HTML avec une variable texte
    :param valeur: objet de type str
    :return: str code html
    """
    return """
<table style="width: 200px">
    <tr>
        <td><strong>Id : </strong>{}</td>
    </tr>
     <tr>
        <td><strong>Name : </strong>{}</td>
    </tr>
     <tr>
        <td><strong>Capacité : </strong>{}</td>
    </tr>
    <tr>
        <td><strong>Velib Dispo : </strong>{}</td>
    </tr>
    <tr>
        <td><strong>Velib electrique : </strong>{}</td>
    </tr>
    <tr>
        <td><strong>Velib mecanique : </strong>{}</td>
    </tr>
    <tr>
        <td><strong>Dernière MAJ : </strong>{}</td>
    </tr>
</table>
""".format(a, b, c, d, e, f, g)


# Fonction d'ouverture du fichier GeoJson
def openJson(chemin):
    with open(chemin) as f:
        lect = json.load(f)
        limite = shape(lect["features"][0]['geometry'])
    return limite


# 3-Fonction Principale
def createMap():
    # Recuperation des donnees sur le site
    stationsVelib, velibStatus, temps = recupData(url), recupData(urlStatus), datetime.now()
    # temps de recuperation et Nom du fichier
    nom = temps.strftime("%Y%m%d_%H_%M_%S")

    # Ouverture du fichier dep 93
    dep = openJson(cheminDep)

    # Fusion des données
    donnees = mergeData(stationsVelib, velibStatus)

    # initialiser la carte centré sur la France
    myMap = folium.Map(location=position,
                       zoom_start=zoom,
                       tiles=fond, attr="fond_OSM")
    # Création des clusters et ajout a la Map
    myCluster = folium.plugins.MarkerCluster().add_to(myMap)
    #folium.GeoJson(configparser["DEFAULT"]["limite"], name='geojson').add_to(myMap)
    folium.GeoJson(dep, name='geojson').add_to(myMap)

    # Boucle sur l'element sations
    for station in donnees:
        # recuperation des coordonnées
        lat = station['lat']
        long = station['lon']
        dispo = station['num_bikes_available']
        ebik = station['ebike']
        # creation d'un point avec la classe Point de shapely
        p = Point(long, lat)

        # Condition de filtre des station du 93
        if dep.contains(p) and dispo >= 8 and ebik >= 1:
            x, y, z, m, k, d, c = station["name"], station["capacity"], station["station_id"], \
                                  dispo, ebik, station["mechanical"], \
                                  station["last_reported"]
            folium.Marker([lat, long],
                          popup=mapopup(z, x, y, m, k, d, c),
                          icon=folium.Icon(icon='bicycle', prefix='fa', color='black')
                          ).add_to(myCluster)
    myMap.save("index_{}.html".format(nom))


if __name__ == "__main__":
    createMap()