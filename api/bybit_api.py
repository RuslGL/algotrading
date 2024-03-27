import requests


class AccessData():

    main_url = "https://api.bybit.com"

    endpoints = {
        'get_all_tickets': '/v5/market/tickers',
        'get_orderbook': '/v5/market/orderbook',
    }

    def get_endpoint(self, endpoint, method='get', params=None):

        if method == 'get':
            response = requests.get(
               url=self.main_url + endpoint, params=params
               )
            return response.json()


class AccessDataSpot(AccessData):

    def __init__(self):
        # super().__init__()
        # раскрыть, если переопределим конструктор родителя
        self.params = {'category': 'spot'}

    def get_all_tickets(self):
        endpoint = self.endpoints['get_all_tickets']
        requested_data = self.get_endpoint(
            endpoint, params=self.params
            )['result']['list']
        return [element['symbol'] for element in requested_data]

    def get_order_book(self, symbol='BTCUSDT', limit=1):
        endpoint = self.endpoints['get_orderbook']
        params = self.params.copy()
        params['symbol'] = symbol
        params['limit'] = limit
        return self.get_endpoint(endpoint, params=params)


class AccessDataFutures(AccessData):

    def __init__(self):
        # super().__init__()
        # раскрыть, если переопределим конструктор родителя
        self.params = {'category': 'linear'}
