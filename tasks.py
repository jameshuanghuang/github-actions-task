import requests
import http.client
import pandas as pd
import logging
import os
import random
import json
import datetime
from datetime import timedelta

logger1 = logging.getLogger('logger1')
logger1.setLevel(logging.INFO)
handler1 = logging.FileHandler('status.log')
handler1.setLevel(logging.INFO)
formatter1 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler1.setFormatter(formatter1)
logger1.addHandler(handler1)

logger2 = logging.getLogger('logger2')
logger2.setLevel(logging.INFO)
handler2 = logging.FileHandler('status_signal.log')
handler2.setLevel(logging.INFO)
formatter2 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler2.setFormatter(formatter2)
logger2.addHandler(handler2)

class Client:
    API_URL = "https://api.finnhub.io/api/v1"
    DEFAULT_TIMEOUT = 10

    def __init__(self, api_key, proxies=None):
        self._session = self._init_session(api_key, proxies)

    @staticmethod
    def _init_session(api_key, proxies):
        session = requests.session()
        session.headers.update({"Accept": "application/json",
                                "User-Agent": "finnhub/python"})
        session.params = {"token": api_key}
        if proxies is not None:
            session.proxies.update(proxies)
        return session

    def _request(self, method, endpoint, params=None):
        url = f"{self.API_URL}/{endpoint}"
        response = self._session.request(method, url, params=params, timeout=self.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_upcoming_ipo(self, start_date, end_date):
        params = {
            'from': start_date,
            'to': end_date
        }
        return self._request('GET', 'calendar/ipo', params=params)
    
def lottery(date):
    x = random.sample(range(1, 50), 5)
    logger1.info(f"The lottery numbers for {date} are: {x[:-1]} and the bonus number is: {x[-1]}")
    return x 

def get_pools(API_KEY):
    conn = http.client.HTTPSConnection("cardano-mainnet.blockfrost.io")
    headers = { 'Project_id': API_KEY }
    
    conn.request("GET", "/api/v0/pools", headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status == 200:
        pools = data.decode("utf-8")
        logger1.info(f"Successfully retrieved pools: {pools}")
        return pools
    else:
        logger1.error(f"Failed to retrieve pools: {res.status} - {data.decode('utf-8')}")
        return None

def convert_timestamp(timestamp):
    dt_object = datetime.datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M')
    return dt_object

def get_fear_and_greed_historical(api_key, start=1, limit=10):
    url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    params = {
        'start': start,
        'limit': limit
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        signal(data)
        logger1.info(f"Successfully retrieved Fear and Greed Index.")
        return data
    else:
        logger1.error(f"Failed to retrieve data: {response.status_code} - {response.text}")
        return None

def get_crypto_listings(api_key, start=1, limit=100, price_min=None, price_max=None, market_cap_min=None, market_cap_max=None, volume_24h_min=None, volume_24h_max=None, circulating_supply_min=None, circulating_supply_max=None, percent_change_24h_min=None, percent_change_24h_max=None, self_reported_circulating_supply_min=None, self_reported_circulating_supply_max=None, self_reported_market_cap_min=None, self_reported_market_cap_max=None, unlocked_market_cap_min=None, unlocked_market_cap_max=None, unlocked_circulating_supply_min=None, unlocked_circulating_supply_max=None, convert=None, convert_id=None, sort='market_cap', sort_dir='desc', cryptocurrency_type='all', tag='all', aux=None):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    params = {
        'start': start,
        'limit': limit,
        'price_min': price_min,
        'price_max': price_max,
        'market_cap_min': market_cap_min,
        'market_cap_max': market_cap_max,
        'volume_24h_min': volume_24h_min,
        'volume_24h_max': volume_24h_max,
        'circulating_supply_min': circulating_supply_min,
        'circulating_supply_max': circulating_supply_max,
        'percent_change_24h_min': percent_change_24h_min,
        'percent_change_24h_max': percent_change_24h_max,
        'self_reported_circulating_supply_min': self_reported_circulating_supply_min,
        'self_reported_circulating_supply_max': self_reported_circulating_supply_max,
        'self_reported_market_cap_min': self_reported_market_cap_min,
        'self_reported_market_cap_max': self_reported_market_cap_max,
        'unlocked_market_cap_min': unlocked_market_cap_min,
        'unlocked_market_cap_max': unlocked_market_cap_max,
        'unlocked_circulating_supply_min': unlocked_circulating_supply_min,
        'unlocked_circulating_supply_max': unlocked_circulating_supply_max,
        'convert': convert,
        'convert_id': convert_id,
        'sort': sort,
        'sort_dir': sort_dir,
        'cryptocurrency_type': cryptocurrency_type,
        'tag': tag,
        'aux': aux
    }
    
    params = {k: v for k, v in params.items() if v is not None}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        signal_track_supply_by_tags(data, 'world-liberty-financial-portfolio')
        signal_track_supply_by_tags(data, 'real-world-assets')
        logger1.info(f"Successfully retrieved crypto listings.")
        return data
    else:
        logger1.error(f"Failed to retrieve data: {response.status_code} - {response.text}")
        return None
        
def signal(data):
    mp = {}
    counter = len(data['data'])
    index_avg = 0
    for item in data['data']:
        if item['value_classification'] in mp:
            mp[item['value_classification']] += 1 / counter
        else:
            mp[item['value_classification']] = 1 / counter
        
        index_avg += item['value'] / counter
    
    fear = mp.get('Fear', 0)
    extreme_fear = mp.get('Extreme Fear', 0)
    greed = mp.get('Greed', 0)
    extreme_greed = mp.get('Extreme Greed', 0)

    if fear + extreme_fear > 0.5:
        logger2.info(f"The average of FGI for the last {counter} days is {index_avg:.2f}, the market sentiment seems Fear")
        if extreme_fear > 0.5:
            logger2.info(f"Consider buy in")
            return "Buy"
    elif greed + extreme_greed > 0.5:
        logger2.info(f"The average of FGI for the last {counter} days is {index_avg:.2f}, the market sentiment seems Greed")
        if extreme_greed > 0.5:
            logger2.info(f"Consider sell out")
            return "Sell"
    else:
        logger2.info(f"The average of FGI for the last {counter} days is {index_avg:.2f}, the market sentiment seems Neutral")
        return "Hold"

def signal_track_supply_by_tags(data, tag):
    scale = 1_000_000_000
    total_circulating_supply = 0
    total_total_supply = 0
    total_market_cap = 0
    symbol = []

    for item in data['data']:
        if 'tags' in item and tag in item['tags']:
            circulating_supply = item.get('circulating_supply', 0)
            total_supply = item.get('total_supply', 0)
            market_cap = item.get('quote', {}).get('USD', {}).get('market_cap', 0)
            
            total_circulating_supply += circulating_supply /scale
            total_total_supply += total_supply /scale
            total_market_cap += market_cap /scale
            
            symbol.append(item['symbol'])

    logger2.info(f"{tag} includes: {symbol}")
    logger2.info(f"Tags: {tag}, Total Circulating Supply (billions): {total_circulating_supply:.2f}, Total Total Supply (billions): {total_total_supply:.2f}, Total Market Cap (billions): {total_market_cap:.2f}")

def signal_ipo(data):
    count_withdrawn, count_priced, count_expected, count_filed = 0, 0, 0, 0
    total_shares_value = 0
    largest_ipo = {"name": "", "status": "", "totalSharesValue": 0}
    latest_withdrawn = {"name": "", "date": ""}
    latest_priced = {"name": "", "date": "", "totalSharesValue": 0}

    for item in data['ipoCalendar']:
        name = item.get('name', '')
        totalSharesValue = item.get('totalSharesValue', 0)
        status = item.get('status', '')
        date = item.get('date', '')

        if totalSharesValue:
            total_shares_value += totalSharesValue
            if totalSharesValue > largest_ipo["totalSharesValue"]:
                largest_ipo = {"name": name, "status": status, "totalSharesValue": totalSharesValue}

        if status == 'priced':
            count_priced += 1
            if not latest_priced["date"] or date > latest_priced["date"]:
                latest_priced = {"name": name, "date": date, "totalSharesValue": totalSharesValue}
        elif status == 'filed':
            count_filed += 1
        elif status == 'expected':
            count_expected += 1
        elif status == 'withdrawn':
            count_withdrawn += 1
            if not latest_withdrawn["date"] or date > latest_withdrawn["date"]:
                latest_withdrawn = {"name": name, "date": date}

    a = (count_priced + count_expected)
    b = (count_priced + count_expected + count_filed)
    c = count_priced
    d = (count_priced + count_expected)

    logger2.info(f"For the last 14 days, {a} / {b} companies filed IPO with price, {c} / {d} IPOs are expected, Total IPOs value: {total_shares_value/1e6:.3f}M")
    logger2.info(f"Largest IPO: {largest_ipo['name']} with totalSharesValue: {largest_ipo['totalSharesValue']/1e6:.3f}M")
    logger2.info(f"Latest IPO is {latest_priced['name']} on {latest_priced['date']} with totalSharesValue: {latest_priced['totalSharesValue']/1e6:.3f}M")
    logger2.info(f"Latest IPO withdrawn: {latest_withdrawn['name']} on {latest_withdrawn['date']}")

    result = (c, d)
    return result

if __name__ == "__main__":

    try:
        API_KEY = os.environ["API_KEY"]
    except KeyError:
        API_KEY = ""
        logger1.error("API_KEY not found in env.")

    try:
        CMC_API_KEY = os.environ["CMC_API_KEY"]
    except KeyError:
        CMC_API_KEY = ""
        logger1.error("CMC_API_KEY not found in env.")

    try:
        FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]
    except KeyError:
        FINNHUB_API_KEY = ""
        logger1.error("FINNHUB_API_KEY not found in env.")


    today = pd.Timestamp.today().tz_localize('UTC').strftime('%Y-%m-%d')
    data = lottery(today)

    if API_KEY:
        data = get_pools(API_KEY)

    if CMC_API_KEY:
        data =  get_crypto_listings(CMC_API_KEY, start=1, limit=5000, sort='volume_30d', price_min=0.0001, market_cap_min=1_000_000_000 ,sort_dir='desc')
        data = get_fear_and_greed_historical(CMC_API_KEY, start=1, limit=90)

    if FINNHUB_API_KEY:
        client = Client(FINNHUB_API_KEY)
        start_date = (pd.Timestamp.today().tz_localize('UTC') - timedelta(days=14)).strftime('%Y-%m-%d')
        data = client.get_upcoming_ipo(start_date, today)
        if data:
            signal_ipo(data)