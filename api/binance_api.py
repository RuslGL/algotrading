import hashlib
import hmac
import requests
import os

from dotenv import load_dotenv
load_dotenv()


BINANCE_API_KEY = str(os.getenv('binance_api_key'))
BINANCE_SECRET_KEY = str(os.getenv('binance_secret_key'))


class binance_spot():
    main_url = 'https://api2.binance.com'

    def get_endpoint(self, endpoint, method='get', params=None):

        if method == 'get':
            response = requests.get(
               url=self.main_url + endpoint, params=params
               )
            return response.json()


class binance_futures():
    main_url = 'https://fapi.binance.com'

    def get_endpoint():
        pass


# authorized requests drafts

binance_api_key = str(os.getenv('binance_api_key'))
binance_secret_key = str(os.getenv('binance_secret_key'))


BASE_FUTURES_URL = 'https://fapi.binance.com'

ENDPOINTS_FUTURES = {
        'get_server_time': '/fapi/v1/time',
        'get_ticker_price': '/fapi/v1/ticker/price',
        'exchange_information': '/fapi/v1/exchangeInfo',

        'make_order': '/fapi/v1/order',  # post |delete
    }


def get_server_time():
    """
    returns server time
    """

    return requests.get(
        BASE_FUTURES_URL + ENDPOINTS_FUTURES['get_server_time']
        ).json()['serverTime']


def exchange_information(symbol=None):
    """
    returns all information if symbol isn't provided
    returns information on the provided pair if given

    """
    information = requests.get(
        BASE_FUTURES_URL+ENDPOINTS_FUTURES['exchange_information']
        ).json()['symbols']
    if symbol:
        return next(
            (element for element in information
             if element['symbol'] == symbol), None)
    return information


def get_current_price(symbol=None):
    """
    returns all prices if symbol isn't provided
    returns price of the provided pair if given

    """
    information = requests.get(
        BASE_FUTURES_URL + ENDPOINTS_FUTURES['get_ticker_price']
        ).json()
    if symbol:
        return float(next(
            (element for element in information if element['symbol'] == symbol
             ), None)['price'])

    return information


def gen_signature(params):
    param_str = '&'.join([f'{k}={v}' for k, v in params.items()])
    signature = hmac.new(
        bytes(binance_secret_key, "utf-8"),
        param_str.encode("utf-8"),
        hashlib.sha256
        ).hexdigest()
    return signature


def make_limit_order(symbol, price, quantity, direction, timeInForce='GTC'):
    url = BASE_FUTURES_URL + ENDPOINTS_FUTURES['make_order']
    symbol = symbol
    price = price
    quantity = quantity
    timestamp = get_server_time()
    timeInForce = timeInForce

    header = {
        "X-MBX-APIKEY": binance_api_key}

    params = {
        "symbol": symbol,
        "type": "LIMIT",
        "timeInForce": timeInForce,
        "quantity": quantity,
        "price": price,
        "timestamp": timestamp,
    }

    if direction == 'BUY':
        params['side'] = 'BUY'

    if direction == 'SELL':
        params['side'] = 'SELL'
    params['signature'] = gen_signature(params)
    new_order = requests.post(url=url, params=params, headers=header).json()

    return new_order


def cancel_order(symbol, orderId):
    url = BASE_FUTURES_URL + ENDPOINTS_FUTURES['make_order']
    symbol = symbol
    timestamp = get_server_time()

    header = {
        "X-MBX-APIKEY": binance_api_key}

    params = {
        "symbol": symbol,
        "orderId": orderId,
        "timestamp": timestamp,
    }
    params['signature'] = gen_signature(params)
    result = requests.delete(url=url, params=params, headers=header).json()
    return result


if __name__ == '__main__':

    symb = 'AXSUSDT'

    price = get_current_price(symbol=symb)
    buy_price = round(price * 0.99, 3)
    sell_price = round(price * 1.01, 3)
    print(f'текущая цена {price}')
    print(f'цена покупки {buy_price} \n цена  продажи {sell_price}')

    quantity = 1
    buy_result = make_limit_order(
        symb, buy_price, quantity, direction='BUY')
    buy_order_id = buy_result['orderId']
    print(f'id покупки = {buy_order_id}')

    sell_result = make_limit_order(
        symb, sell_price, quantity, direction='SELL')
    sell_order_id = sell_result['orderId']
    print(f'id продажи = {sell_order_id}')

    print(cancel_order(symb, buy_order_id))
    print(cancel_order(symb, sell_order_id))
