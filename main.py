from api import binance_api


# spot endpoints https://binance-docs.github.io/apidocs/spot/en/#general-info
spot_market_ping = '/api/v3/ping'
spot_exchange_info = '/api/v3/exchangeInfo'
spot_24h_statistics = '/api/v3/ticker/24hr'


if __name__ == '__main__':

    # test code
    spot_client = binance_api.binance_spot()
    print(spot_client.get_endpoint(spot_market_ping))
