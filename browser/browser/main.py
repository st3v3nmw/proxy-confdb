import argparse
import json
import subprocess

import html2text
import requests
from connect.utils.terminal.markdown import render


def get_proxy_config():
    config = {}
    for protocol in ["http", "https"]:
        cmd = f"snapctl get --view :proxy-observe {protocol} -d"

        proc = subprocess.run(cmd.split(), capture_output=True, text=True)

        if proc.returncode != 0:
            continue

        config.update(json.loads(proc.stdout))

    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str)
    args = parser.parse_args()
    url: str = args.url

    bypass = []
    proxy_config = get_proxy_config()

    if url.startswith("https"):
        if "https" in proxy_config:
            bypass = proxy_config["https"]["bypass"]
    elif url.startswith("http"):
        if "http" in proxy_config:
            bypass = proxy_config["http"]["bypass"]

    if any(url.startswith(no_proxy_url) for no_proxy_url in bypass):
        response = requests.get(url)
    else:
        response = requests.get(
            url,
            proxies={k: v["url"] for k, v in proxy_config.items()},
        )

    text = html2text.html2text(response.text)
    print(render(text))
