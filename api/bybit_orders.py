import asyncio
import hashlib
import hmac
import json
import os
import time

import aiohttp

from dotenv import load_dotenv

load_dotenv()

BYBIT_API_KEY = str(os.getenv('bybit_api_key'))
BYBIT_SECRET_KEY = str(os.getenv('bybit_secret_key'))


BYBIT_END = {
    'testnet_url': 'https://api-testnet.bybit.com',
    'main_url': 'https://api.bybit.com',
    'place_order': '/v5/order/create',
    'set_leverage': '/v5/position/set-leverage',
    'cancel_order': '/v5/order/cancel'
}




# bybit section

# util functions
async def post_data(url, data, headers):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            return await response.json()


def get_signature_bybit(data, timestamp, recv_wind):
    query = f'{timestamp}{BYBIT_API_KEY}{recv_wind}{data}'
    return hmac.new(BYBIT_SECRET_KEY.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()


async def post_bybit_signed(endpoint, **kwargs):
    timestamp = int(time.time() * 1000)
    #timestamp = bybit_time
    recv_wind = 5000
    data = json.dumps({key: str(value) for key, value in kwargs.items()})
    signature = get_signature_bybit(data, timestamp, recv_wind)
    headers = {
        'Accept': 'application/json',
        'X-BAPI-SIGN': signature,
        'X-BAPI-API-KEY': BYBIT_API_KEY,
        'X-BAPI-TIMESTAMP': str(timestamp),
        'X-BAPI-RECV-WINDOW': str(recv_wind)
    }

    url = BYBIT_END['main_url'] + BYBIT_END[endpoint]

    return await post_data(
        url,
        data, 
        headers)


# set leverage --- WORKS
async def set_leverage_futures(symbol, buyLeverage, sellLeverage):
    result = await post_bybit_signed('set_leverage', category='linear', symbol=symbol, buyLeverage=buyLeverage, sellLeverage=sellLeverage)
    #{'retCode': 0, 'retMsg': 'OK', 'result': {}, 'retExtInfo': {}, 'time': 1712853552195}
    return result


# cancel order
async def cancel_order_futures(symbol, orderId, category):
    result = post_bybit_signed('cancel_order', category=category, symbol=symbol, orderId=orderId)
    #{'retCode': 0, 'retMsg': 'OK', 'result': {'orderId': '25e70057-3e82-4d57-896d-537e51fd9004', 'orderLinkId': ''}, 'retExtInfo': {}, 'time': 1712853599354}
    return await result


#category	true	string	Product type
#Unified account: spot, linear, inverse, option
#Classic account: spot, linear, inverse
#symbol	true	string	Symbol name
#orderId	false	string	Order ID. Either orderId or orderLinkId is required


################################

# bybit spot


# limit order
async def bybit_new_limit_order_spot(symbol, side, quantity, price):
    pass




################################

# bybit futures
# размещаем лимитный фьюч ордер на Bybit - WORKS
async def bybit_new_limit_order_futures(symbol, side, quantity, price):
    result = await post_bybit_signed('place_order', category='linear', symbol=symbol, side=side, qty=quantity,
                                     price=price, orderType='Limit')
    #{'retCode': 0, 'retMsg': 'OK', 'result': {'orderId': '25e70057-3e82-4d57-896d-537e51fd9004', 'orderLinkId': ''}, 'retExtInfo': {}, 'time': 1712853599354}
    return result

async def main():
    pass



# test performance
if __name__ == '__main__':
    symbol = 'BTCUSDT'
    side = 'Buy'
    quantity = 0.001
    price = 50000
    buyLeverage = 1
    sellLeverage = 1
    category = 'linear'
    orderId = '1'

#set_leverage_futures(symbol, buyLeverage, sellLeverage)

#works
    res = asyncio.run(set_leverage_futures(symbol, buyLeverage, sellLeverage))

# works
    #res = asyncio.run(bybit_new_limit_order_futures(symbol, side, quantity, price))

    #res = await cancel_order_futures(symbol, orderId, category)
    #res = asyncio.run(await cancel_order_futures(symbol, orderId, category))

    print(res)

    #res = asyncio.run(cancel_order_futures(symbol, orderId, category))