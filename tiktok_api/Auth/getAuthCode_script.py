import json
from pathlib import Path
import argparse
import webbrowser

def load_config():
    config_path = Path(__file__).parent.parent.parent / 'Config' / 'ToktokConfig' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)["TikTok"]

def build_auth_url(app_key, redirect_uri, region="ES"):
    base_url = "https://auth.tiktok-shops.com/oauth/authorize"
    params = (
        f"app_key={app_key}&"
        f"redirect_uri={redirect_uri}&"
        f"state=xyz&"
        f"response_type=code&"
        f"region={region}"
    )
    return f"{base_url}?{params}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="打开TikTok授权页面")
    parser.add_argument('--region', type=str, default='ES', help='区域代码，默认ES')
    args = parser.parse_args()

    config = load_config()
    auth_url = build_auth_url(config["AppKey"], config["RedirectUri"], args.region)
    print("即将打开TikTok授权页面：")
    print(auth_url)
    webbrowser.open(auth_url)
    print("如果浏览器未自动打开，请手动复制上面的链接到浏览器访问。") 