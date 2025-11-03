import requests
import json
from pathlib import Path



def parse_response(response):
    json_response = json.loads(response.text)
    items_in_basket = json_response['payload']['cartItems']
    for item in items_in_basket:
        if item['id'] == '69074757c6604d1065cc0f6e':
            print(item['price']['amount'])
            pope = 120027

def get_price_data():

    base = Path(__file__).resolve().parent
    token_path = base / "token" / "token.txt"
    with open(token_path, "r", encoding="utf-8") as f:
        cookies = f.read().strip()
    headers = {
        'authorization': cookies,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }
    json_data = {
        'couponSelection': {
            'byDefault': {},
        },
    }

    response = requests.post('https://www.joom.ru/api/1.1/cart/get', headers=headers, json=json_data)
    if response.status_code == 200:
        parse_response(response)

if __name__ == "__main__":
    get_price_data()