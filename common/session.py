import json
import requests
from config.config import API_URL, USERNAME, PASSWORD


def get_session():
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,vi;q=0.8,en-US;q=0.7,en;q=0.6,ko;q=0.5,ja;q=0.4",
        "cache-control": "no-cache",
        "content-length": "0",
        "origin": "https://www.google.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.google.com",
        "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-storage-access": "active",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "content-type": "application/json"
    }

    url = API_URL + "/api/login"

    data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    data = json.dumps(data, separators=(',', ':'))

    session = requests.Session()

    response = session.post(url, headers=headers, data=data)

    print("请求状态码:", response.status_code)
    print("模拟登录回调:", response.text)

    if response.status_code != 200:
        print("登录失败")
        exit()

    if "Logged in" not in response.text:
        print("登录失败")
        exit()

    return session
