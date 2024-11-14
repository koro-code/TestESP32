from flask import Flask, request, jsonify
import os
import httpx
from dotenv import load_dotenv
import tempfile

app = Flask(__name__)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration pour Microsoft Graph API
APPLICATION_ID = os.getenv('APPLICATION_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID')

SCOPES = ['https://graph.microsoft.com/.default']
MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'

def get_access_token():
    token_url = f'https://login.microsoftonline.com/{TENANT_ID}'
    data = {
        'grant_type': 'client_credentials',
        'client_id': APPLICATION_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = httpx.post(token_url, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def upload_file(headers, file_path, folder_path=None, if_exists='rename'):
    base_name = os.path.basename(file_path)
    if folder_path:
        # Construire le chemin complet encodé pour l'URL
        encoded_folder_path = folder_path.replace('/', '%2F').replace(' ', '%20')
        url = f'{MS_GRAPH_BASE_URL}/me/drive/root:/{encoded_folder_path}%2F{base_name}:/content'
    else:
        url = f'{MS_GRAPH_BASE_URL}/me/drive/root:/{base_name}:/content'

    params = {}
    if if_exists == 'rename':
        params['@microsoft.graph.conflictBehavior'] = 'rename'
    elif if_exists == 'replace':
        params['@microsoft.graph.conflictBehavior'] = 'replace'

    with open(file_path, 'rb') as file:
        response = httpx.put(url, headers=headers, params=params, content=file)
        response.raise_for_status()
        return response.json()

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    print(f"Données reçues : Température={temperature}, Humidité={humidity}")

    try:
        access_token = get_access_token()
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/octet-stream'
        }

        # Créer un fichier temporaire avec les données reçues
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(f"Température: {temperature} C, Humidité: {humidity}%\n")
            temp_file_path = temp_file.name

        # Spécifier le chemin du dossier dans OneDrive
        folder_path = '/Documents/Applications/StationMeteo'

        # Uploader le fichier sur OneDrive
        file_metadata = upload_file(headers, temp_file_path, folder_path=folder_path, if_exists='replace')

        # Supprimer le fichier temporaire
        os.remove(temp_file_path)

        # Afficher les informations du fichier uploadé
        print(f'Fichier uploadé avec succès. ID: {file_metadata["id"]}')

        return jsonify({'status': 'Données reçues et enregistrées sur OneDrive'}), 200

    except Exception as e:
        print(f"Erreur lors de l'accès à OneDrive : {e}")
        return jsonify({'error': f'Erreur lors de l\'accès à OneDrive : {e}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
