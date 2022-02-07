# 1) imports
import configparser
import sys
import os
import argparse

fichier = "./config.ini"
# 5.1) Arguments
parser=argparse.ArgumentParser(description="indique la section du ficher de config par defaut")
parser.add_argument("limite",help="Couche geojson du departement 93")
args = parser.parse_args()
configparser = configparser.ConfigParser()
configparser.read(fichier)

# test si le chemin correspond bien à quelque chose
if os.path.exists(fichier):
    # si c'est le cas c'est que le fichier existe on peut continuer
    configparser.read(fichier)
else:
    # si le fichier n'existe pas : stop avec message
    sys.exit("fichier de configuration non trouvé: {}, arrêt du script".format(fichier))
