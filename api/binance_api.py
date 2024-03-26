import requests


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
