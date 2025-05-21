import os

def create_tiktok_api_app():
    try:
        print("开始创建目录和文件...")

        ROOT_DIR = os.getcwd()
        APP_NAME = 'tiktok_api'
        app_dir = os.path.join(ROOT_DIR, APP_NAME)
        os.makedirs(app_dir, exist_ok=True)

        files = {
            '__init__.py': '',
            'admin.py': 'from django.contrib import admin\n\n# Register your models here.\n',
            'apps.py': f"""from django.apps import AppConfig

class TiktokApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{APP_NAME}'
""",
            'models.py': 'from django.db import models\n\n# Create your models here.\n',
            'views.py': """from django.http import JsonResponse
from django.views import View

# 这里后续添加视图逻辑
""",
            'urls.py': """from django.urls import path
from . import views

urlpatterns = [
    # path('', views.YourView.as_view(), name='your_view'),
]
""",
            'tiktok_client.py': """import json
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
""",
            'utils.py': """# 辅助函数可以写这里
"""
        }

        for filename, content in files.items():
            filepath = os.path.join(app_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        token_file_path = os.path.join(app_dir, 'token_storage.json')
        if not os.path.exists(token_file_path):
            with open(token_file_path, 'w', encoding='utf-8') as f:
                f.write('{}')

        print(f"App '{APP_NAME}' 目录结构已创建完成，路径：{app_dir}")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    create_tiktok_api_app()
