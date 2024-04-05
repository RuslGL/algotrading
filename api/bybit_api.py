import hashlib
import hmac
import json
# import time
import requests
import os

from dotenv import load_dotenv

load_dotenv()

BYBIT_API_KEY = str(os.getenv('bybit_api_key'))
BYBIT_SECRET_KEY = str(os.getenv('bybit_secret_key'))


class AccessMarketData():

    main_url = 'https://api.bybit.com'

    endpoints = {
        # market endpoints
        'get_server_time': '/v5/market/time',
        'get_tickers': '/v5/market/tickers',
        'get_orderbook': '/v5/market/orderbook',
        'get_instruments_info': '/v5/market/instruments-info',
        'get_server_time': '/v5/market/time',

        # trade enpoints
        'create_order': '/v5/order/create',
        'cancel_order': '/v5/order/cancel',

    }
    
    def get_endpoint(self, endpoint, method='get', params=None):

        if method == 'get':
            response = requests.get(
               url=self.main_url + endpoint, params=params
               )
            return response.json()

    def get_server_time(self):
        endpoint = self.endpoints['get_server_time']
        return self.get_endpoint(endpoint).get('time')      

    def get_all_tickers(self, category='spot'):
        endpoint = self.endpoints['get_tickers']
        params = {
            'category': category
        }
        
        requested_data = self.get_endpoint(
            endpoint, params=params
            )['result']['list']
        return [element['symbol'] for element in requested_data]

    def get_ticker_info(self, symbol='BTCUSDT', category='spot'):
        endpoint = self.endpoints['get_tickers']
        params = {
            'category': category,
            'symbol': symbol,
        }
        
        requested_data = self.get_endpoint(
            endpoint, params=params
            )
        return requested_data.get('result').get('list')[0]

    def get_order_book(self, symbol='BTCUSDT', category='spot', limit=1):
        endpoint = self.endpoints['get_orderbook']
        params = {
            'category': category,
            'symbol': symbol,
            'limit': limit
            }
        return self.get_endpoint(endpoint, params=params)
    
    def get_instruments_info(self, symbol='BTCUSDT', category='spot'):
        endpoint = self.endpoints['get_instruments_info']
        params = {
            'category': category,
            'symbol': symbol,
        }
        return self.get_endpoint(endpoint, params=params)


# private api, signature functions

def gen_signature(params, timestamp):
    param_str = timestamp + BYBIT_API_KEY + '5000' + json.dumps(params)
    signature = hmac.new(bytes(BYBIT_SECRET_KEY, "utf-8"), param_str.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature

def create_limit_order(side, symbol, price, quantity, category):
    timestamp  = str(AccessMarketData().get_server_time()) 
    url_buy = 'https://api.bybit.com' + '/v5/order/create'


    header = {
        'X-BAPI-API-KEY': BYBIT_API_KEY,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': "5000"
    }

    params = {
        "category": category,
        "symbol": symbol,
        "side": side,
        "orderType": "Limit",
        "qty": str(quantity),
        "price": str(price),
    }

    header["X-BAPI-SIGN"] = gen_signature(params, timestamp)
    return requests.post(url_buy, headers=header, data=json.dumps(params)).json()


def cancel_order(category, symbol, order_id):
    timestamp  = str(AccessMarketData().get_server_time())
    #timestamp = str(int(time.time() * 1000)) 
    url_cancel = 'https://api.bybit.com' + '/v5/order/cancel'


    header = {
        'X-BAPI-API-KEY': BYBIT_API_KEY,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': "5000"
    }

    params = {
        'category': category,
        'symbol': symbol,
        'orderId': order_id

    }

    header['X-BAPI-SIGN'] = gen_signature(params, timestamp)
    return requests.post(url_cancel, headers=header, data=json.dumps(params)).json()


# пример исполнения кода
if __name__ == '__main__':

    symbol = 'ADAUSDT'

    connector = AccessMarketData()
    prices = connector.get_ticker_info(symbol=symbol, category='linear')

    bid_price = prices.get('bid1Price')
    ask_price = prices.get('ask1Price')
    print('\n', bid_price, ask_price)

    min_order = 1
    tick_size = 0.0001

    quantity_one = min_order
    quantity_two = min_order * 2

    purchase_price_first = round(float(bid_price) * 0.99, 4)
    purchase_price_second = round(float(bid_price) * 0.98, 4)


    print('Purchase prices', purchase_price_first, purchase_price_second)

    side = "Buy",
    category = 'linear'

    # Размещаем лимитный ордер на покупку
    result = create_limit_order(side=side, symbol=symbol, price=purchase_price_first, quantity=quantity_one, category=category)

    order_id_first  = result.get('result').get('orderId')
    print(order_id_first)

    # Отменяем лимитный ордер на покупку
    result_canc = cancel_order(category, symbol, order_id_first)
    print(result_canc)

