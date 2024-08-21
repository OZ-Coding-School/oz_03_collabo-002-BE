import requests


def get_exchange_rate(api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}")

    data = response.json()
    return data["conversion_rates"]


def convert_to_usd(price_in_local_currency, exchange_rate):
    return price_in_local_currency / exchange_rate
