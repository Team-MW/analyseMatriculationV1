from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import logging

from ocr_engine import extract_text
from api.database import get_info_by_plaque
from api.models import create_table

app = Flask(__name__)
CORS(app)
create_table()

logging.basicConfig(level=logging.INFO)

# Déclare une route Flask accessible via POST à l'URL /ocr
@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        # Vérifie si le champ 'image' est présent dans les fichiers envoyés
        if 'image' not in request.files:
            logging.warning("Aucune image reçue")
            # Retourne une erreur 400 si aucun fichier image n'est fourni
            return jsonify({'error': 'Aucun fichier image reçu'}), 400

        # Récupère le fichier image depuis la requête
        image_file = request.files['image']
        # Lit le contenu du fichier en bytes
        image_bytes = image_file.read()
        # Ouvre l'image à partir des bytes en mémoire
        image = Image.open(io.BytesIO(image_bytes))

        # Extrait le texte OCR de l'image, supprime les espaces et met en majuscules
        informationOCR = extract_text(image_bytes).replace(" ", "").upper()
        logging.info(f"Texte extrait : {informationOCR}")

        # Recherche les informations associées à la plaque extraite
        info = get_info_by_plaque(informationOCR)
        if info:
            # Si la plaque est reconnue, construit une réponse positive
            response = {
                'text': informationOCR,
                'statut': 'Autorisé',
                'proprietaire': info[0]  # Nom ou identifiant du propriétaire
            }
            logging.info(f"✅ Plaque '{informationOCR}' reconnue : Autorisé ({info[0]})")
        else:
            # Si la plaque est inconnue, construit une réponse négative
            response = {
                'text': informationOCR,
                'statut': 'Non autorisé',
                'message': 'Plaque inconnue'
            }
            logging.info(f" Plaque '{informationOCR}' non reconnue : Interdit")

        # Log de la réponse finale envoyée au client
        logging.info(f"Réponse envoyée : {response}")
        # Retourne la réponse JSON au client
        return jsonify(response)

    except Exception as e:
        # Capture toute erreur inattendue et retourne une erreur 500
        logging.error(f"Erreur OCR : {str(e)}")
        return jsonify({'error': 'Erreur interne'}), 500

# Point d'entrée de l'application Flask
#if __name__ == '__main__':
    # Lance le serveur Flask en mode debug sur le port 8080
#   app.run(debug=True, port=8070)

    # commentaire générél
    # L32: La ligne 32 utilise la fonction get_info_by_plaque pour vérifier si
    # la plaque extraite par OCR est présente dans la base de données.
    # Si elle est trouvée, les informations du propriétaire sont récupérées et incluses
    # dans la réponse JSON envoyée au client. Si la plaque n'est pas trouvée, une réponse i
    # ndiquant que la plaque est "Non autorisé" est renvoyée.
