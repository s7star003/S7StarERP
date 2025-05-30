import json
from pathlib import Path
import argparse
import webbrowser
import base64
import time
import os
import shutil
import subprocess

def load_config():
    config_path = Path(__file__).parent.parent.parent / 'Config' / 'SheinConfig' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)["Shein"]

def build_auth_url(appid, redirect_url):
    auth_url = "https://openapi-sem.sheincorp.com/#/empower"
    state = f"AUTH-SHEIN-{int(time.time() * 1000)}"
    redirect_url_b64 = base64.b64encode(redirect_url.encode("utf-8")).decode("utf-8")
    url = f"{auth_url}?appid={appid}&redirectUrl={redirect_url_b64}&state={state}"
    return url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="打开SHEIN授权页面")
    args = parser.parse_args()

    config = load_config()
    auth_url = build_auth_url(config["AppKey"], config["RedirectUri"])
    print("即将打开SHEIN授权页面：")
    print(auth_url)
    # 优先尝试用主流浏览器新开窗口
    browser_paths = [
        ("chrome", [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]),
        ("edge", [
            r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
        ]),
        ("firefox", [
            r"C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            r"C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
        ])
    ]
    opened = False
    for name, paths in browser_paths:
        for path in paths:
            if os.path.exists(path):
                subprocess.Popen([path, '--new-window', auth_url])
                opened = True
                break
        if opened:
            break
    if not opened:
        # 未检测到已知浏览器，回退到默认方式
        webbrowser.open(auth_url)
    print("如果浏览器未自动打开，请手动复制上面的链接到浏览器访问。") 