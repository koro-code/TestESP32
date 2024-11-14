from flask import Flask, request, jsonify
from O365 import Account, FileSystemTokenBackend
import os

app = Flask(__name__)

# Configuration pour O365
CLIENT_ID = os.getenv('APPLICATION_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TOKEN_BACKEND = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')
SCOPES = ['offline_access', 'Files.ReadWrite']

credentials = (CLIENT_ID, CLIENT_SECRET)
account = Account(credentials, token_backend=TOKEN_BACKEND)

if not account.is_authenticated:
    account.authenticate(scopes=SCOPES, redirect_uri='http://localhost:5000/redirect')

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    print(f"Données reçues : Température={temperature}, Humidité={humidity}")

    if account.is_authenticated:
        storage = account.storage()
        drive = storage.get_default_drive()
        file_name = 'data.txt'
        file_path = '/' + file_name  # Chemin du fichier dans OneDrive

        try:
            # Essayer de récupérer le fichier existant
            file = drive.get_item_by_path(file_path)

            if file is None:
                # Le fichier n'existe pas, le créer avec le contenu initial
                new_content = f"Température: {temperature} C, Humidité: {humidity}%\n"
                root_folder = drive.get_root_folder()
                # Créer le fichier avec le contenu initial
                new_file = root_folder.create_child(name=file_name, file=True)
                new_file.upload_content(new_content.encode('utf-8'))
                print("Fichier créé avec succès.")
            else:
                # Lire le contenu existant
                content = file.get_content()
                existing_content = content.decode('utf-8') if content else ''
                # Ajouter les nouvelles données
                new_content = existing_content + f"Température: {temperature} C, Humidité: {humidity}%\n"
                # Mettre à jour le fichier en téléversant le nouveau contenu
                file.upload_content(new_content.encode('utf-8'))
                print("Données écrites dans le fichier sur OneDrive.")

            return jsonify({'status': 'Données reçues et enregistrées sur OneDrive'}), 200

        except Exception as e:
            print(f"Erreur lors de l'accès à OneDrive : {e}")
            return jsonify({'error': f'Erreur lors de l\'accès à OneDrive : {e}'}), 500

    else:
        return jsonify({'error': 'Non authentifié avec OneDrive'}), 401

@app.route('/redirect')
def redirect_handler():
    return 'Authentification réussie ! Vous pouvez fermer cette page.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
