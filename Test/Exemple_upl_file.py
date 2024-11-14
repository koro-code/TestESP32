import os
from pathlib import Path
import httpx
from dotenv import load_dotenv
from ms_graph import get_access_token, MS_GRAPH_BASE_URL

def upload_file(headers, file_path, folder_id=None, if_exists='rename'):
    base_name = os.path.basename(file_path)
    url = f'{MS_GRAPH_BASE_URL}/me/drive/root:/{base_name}:/content'
    if folder_id:
        url = f'{MS_GRAPH_BASE_URL}/me/drive/items/{folder_id}:/{base_name}:/content'

    if if_exists == 'rename':
        headers['Content-Type'] = 'application/octet-stream'
        params = {
            '@microsoft.graph.conflictBehavior': 'rename'
        }
    elif if_exists == 'replace':
        params = {}
    else:
        return None

    with open(file_path, 'rb') as file:
        response = httpx.put(url, headers=headers, params=params, data=file)

    if response.status_code in (200, 201):
        print(f'File "{file_path}" uploaded successfully')
        return response.json()
    else:
        print(f'Failed to upload file "{file_path}"')
        print('Description:')
        print(response.json()['error']['message'])

def main():
    load_dotenv()
    APPLICATION_ID = os.getenv('APPLICATION_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    SCOPES = ['User.Read', 'Files.ReadWrite.All']

    try:
        access_token = get_access_token(
            application_id=APPLICATION_ID, 
            client_secret=CLIENT_SECRET, 
            scopes=SCOPES
        )
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        asset_folder = Path('assets')
        file = asset_folder / 'file.log'
        file_path = str(file)

        folder_id = '5314DE38EA71F397!22545'
        file_metadata = upload_file(headers, file_path, folder_id, if_exists='replace')
        if file_metadata:
            print(f'File id: {file_metadata["id"]}')
            print(f'File parent id: {file_metadata["parentReference"]["path"]}')
            print(f'File web url: {file_metadata["webUrl"]}')
            print('-' * 50)         
    
    except Exception as e:
        print(f'Error: {e}')

main()