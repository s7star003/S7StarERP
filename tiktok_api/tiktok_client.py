import json
import time
import requests
from pathlib import Path

TOKEN_FILE = Path(__file__).parent / 'token_storage.json'

def save_token_to_file(token_data):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)

def load_token_from_file():
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)

def get_access_token(auth_code):
    # TODO: 替换成真实请求
    response = requests.post('https://open.tiktokapis.com/oauth/access_token', data={
        'client_key': 'YOUR_APP_KEY',
        'client_secret': 'YOUR_APP_SECRET',
        'code': auth_code,
        'grant_type': 'authorization_code'
    })
    token_data = response.json()
    token_data['obtained_at'] = int(time.time())
    save_token_to_file(token_data)
    return token_data

def is_token_expired(token_data):
    return (int(time.time()) - token_data['obtained_at']) >= token_data['expires_in']

def get_order_list():
    token_data = load_token_from_file()
    if not token_data or is_token_expired(token_data):
        raise Exception("Token expired or not found")
    access_token = token_data['access_token']
    response = requests.get('https://open.tiktokapis.com/order/list', headers={
        'Access-Token': access_token
    })
    return response.json()
