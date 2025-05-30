import json
from pathlib import Path
import argparse
import webbrowser
import os
import subprocess
import uuid
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def load_config():
    config_path = Path(__file__).parent.parent.parent / 'Config' / 'MiraviaConfig' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)["Miravia"]

def get_auth_url():
    config = load_config()
    base_url = config["OauthSignin"]
    # 生成新的 state、nonce、timestamp
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    timestamp = str(int(time.time()))
    # 解析原始URL，追加/替换参数
    url_parts = list(urlparse(base_url))
    query = parse_qs(url_parts[4])
    query['state'] = [state]
    query['nonce'] = [nonce]
    query['timestamp'] = [timestamp]
    url_parts[4] = urlencode(query, doseq=True)
    return urlunparse(url_parts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="打开Miravia授权页面")
    args = parser.parse_args()

    auth_url = get_auth_url()
    print("即将打开Miravia授权页面：")
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
