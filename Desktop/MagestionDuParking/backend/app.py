from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import logging

from ocr_engine import extract_text # Parametre modele OCR
from api.database import get_info_by_plaque  # Cherche les info de la plaque dans data base
from api.modelsTeste import create_table # Temporaire

app = Flask(__name__)
CORS(app)
create_table()

demandes = []



logging.basicConfig(level=logging.INFO)

# Déclare une route Flask accessible via POST à l'URL /ocr
@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        #  Cas d'envoi manuel (champ text)
        if 'text' in request.form:
            plaque_text = request.form['text'].replace(" ", "").upper()
            logging.info(f"Plaque reçue manuellement : {plaque_text}")

            info = get_info_by_plaque(plaque_text)
            if info:
                response = {
                    'text': plaque_text,
                    'statut': 'Autorisé',
                    'proprietaire': info[0]
                }
            else:
                response = {
                    'text': plaque_text,
                    'statut': 'Non autorisé',
                    'message': 'Plaque inconnue'
                }

            return jsonify(response)

        #  Sinon, cas d'image (via caméra)
        if 'image' not in request.files:
            logging.warning("Aucune image reçue")
            return jsonify({'error': 'Aucun fichier image reçu'}), 400

        image_file = request.files['image']
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))

        informationOCR = extract_text(image_bytes).replace(" ", "").upper()
        logging.info(f"Texte extrait : {informationOCR}")

        info = get_info_by_plaque(informationOCR)
        if info:
            response = {
                'text': informationOCR,
                'statut': 'Autorisé',
                'proprietaire': info[0]
            }
        else:
            response = {
                'text': informationOCR,
                'statut': 'Non autorisé',
                'message': 'Plaque inconnue'
            }

        return jsonify(response)

    except Exception as e:
        logging.error(f"Erreur OCR : {str(e)}")
        return jsonify({'error': 'Erreur interne'}), 500


@app.route('/register', methods=['POST'])
def register_plate():
    try:
        data = request.get_json()
        plate = data.get('plate', '').replace(" ", "").upper()
        owner = data.get('owner', '')
        company = data.get('company', '')

        if not plate or not owner:
            return jsonify({'success': False, 'message': 'Champs requis manquants'}), 400

        # Enregistre dans la base (à adapter selon ton modèle)
        from api.database import insert_new_plate  # tu dois créer cette fonction

        success = insert_new_plate(plate, owner, company)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Plaque déjà existante'}), 409

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@app.route("/api/visiteur", methods=["POST"])
def ajouter_demande():
    data = request.get_json()
    demandes.append(data)
    return jsonify({"message": "Demande enregistrée avec succès"}), 201

@app.route("/api/visiteur/<user_id>", methods=["GET"])
def get_demandes_user(user_id):
    user_demandes = [d for d in demandes if d.get("userId") == user_id]
    return jsonify(user_demandes)

@app.route("/api/demandes", methods=["GET"])
def get_all_demandes():
    return jsonify(demandes)

@app.route("/api/demandes/<int:index>", methods=["PATCH"])
def update_statut(index):
    data = request.get_json()
    try:
        demandes[index]["statut"] = data.get("statut")
        return jsonify({"message": "Statut mis à jour"})
    except IndexError:
        return jsonify({"error": "Demande non trouvée"}), 404





# Point d'entrée de l'application Flask
if __name__ == '__main__':
    # Lance le serveur Flask en mode debug sur le port 8080
    app.run(debug=True, port=8090)

    # commentaire générél
    # L32: La ligne 32 utilise la fonction get_info_by_plaque pour vérifier si
    # la plaque extraite par OCR est présente dans la base de données.
    # Si elle est trouvée, les informations du propriétaire sont récupérées et incluses
    # dans la réponse JSON envoyée au client. Si la plaque n'est pas trouvée, une réponse i
    # ndiquant que la plaque est "Non autorisé" est renvoyée.
