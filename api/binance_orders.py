import asyncio
import hashlib
import hmac
import os
import time

import aiohttp

from dotenv import load_dotenv


load_dotenv()

IF_TEST = True

if IF_TEST == True:
    BINANCE_API_KEY = str(os.getenv('test_futures_binance_api_key'))
    BINANCE_SECRET_KEY = str(os.getenv('test_futures_binance_secret_key'))
    MAIN_URL = 'https://testnet.binancefuture.com'
else:
    BINANCE_API_KEY = str(os.getenv('binance_api_key'))
    BINANCE_SECRET_KEY = str(os.getenv('binance_secret_key'))
    MAIN_URL = ''


ENDPOINTS_BINANCE = {
        'make_order': '/fapi/v1/order',
        'ping': '/fapi/v1/ping',
        'server_time': '/fapi/v1/time',
}



def get_signature_binance(params, if_test=True):
    if if_test == True:
        secret_key = BINANCE_SECRET_KEY

    param_str = '&'.join([f'{k}={v}' for k, v in params.items()])
    signature = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature



# отправляем POST запрос
async def post_data(url, data, headers, if_test=True):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            return await response.json()



# отправляем POST запрос с подписью на Binance
async def post_binance_signed(endpoint, if_test=True, **kwargs):
    if if_test == True:
        api_key = BINANCE_API_KEY
        url = MAIN_URL + endpoint
    else:
        return (print('Real trade params are not established'))
    
    headers = {
        'Accept': 'application/json',
        'X-MBX-APIKEY': api_key
    }
    kwargs['timestamp'] = int(time.time() * 1000)
    kwargs['signature'] = get_signature_binance(kwargs)
    return await post_data(url, kwargs, headers)


# размещаем ордер на Binance
async def futures_binance_new_order(type, symbol, side, 
                                    quantity=None, price=None, timeInForce=None, 
                                    stop_price=None, reduceOnly=True, newOrderRespType="RESULT", 
                                    closePosition='false', if_test=True):
    """
    Creates orders on futures, by default via testnet
    Following types are available: 'LIMIT', 'MARKET', 'TAKE_PROFIT_PARTIAL_MARKET'
    Arguments for LIMIT: type, symbol, side, quantity, price, timeInForce
    Aguments for MARKET: type, symbol, side, quantity
    Aguments for TAKE_PROFIT_PARTIAL_LIMIT: type, symbol, side, quantity, price, timeInForce, stop_price
    Aguments for TAKE_PROFIT_PARTIAL_MARKET
    Aguments for STOP_MARKET_FULL: type, symbol, side, stop_price
    """


    if type == 'LIMIT':
        result = await post_binance_signed(
            ENDPOINTS_BINANCE.get('make_order'),
            symbol=symbol,
            side=side, 
            price=price, 
            quantity=quantity, 
            type=type,
            timeInForce=timeInForce,
            if_test=if_test,)
    
    if type == 'MARKET':
        result = await post_binance_signed(
            ENDPOINTS_BINANCE.get('make_order'),
            symbol=symbol,
            side=side, 
            quantity=quantity, 
            type='MARKET',
            if_test = if_test,
            newOrderRespType=newOrderRespType),

    if type == 'TAKE_PROFIT_PARTIAL_LIMIT':
        result = await post_binance_signed(
            ENDPOINTS_BINANCE.get('make_order'),
            type='TAKE_PROFIT',
            symbol=symbol,
            side=side, 
            quantity=quantity,
            stopPrice = stop_price,
            price = price, 
            timeInForce=timeInForce,
            if_test = if_test,
            reduceOnly=reduceOnly),
    

    if type == 'TAKE_PROFIT_PARTIAL_MARKET':
        result = await post_binance_signed(
            ENDPOINTS_BINANCE.get('make_order'),
            type='TAKE_PROFIT_MARKET',
            symbol=symbol,
            side=side, 
            quantity=quantity,
            stopPrice = stop_price,
            timeInForce=timeInForce,
            if_test = if_test,
            reduceOnly=reduceOnly),


    if type == 'STOP_MARKET_FULL':
        result = await post_binance_signed(
            ENDPOINTS_BINANCE.get('make_order'),
            type='STOP_MARKET',
            symbol=symbol,
            side=side, 
            stopPrice = stop_price,
            closePosition = closePosition,
            if_test = if_test,
        )

    return result


def get_price_market_order(data):
    return float(data[0].get('avgPrice'))




if __name__ == '__main__':
    async def main():

        timeInForce = 'GTC'
        symbol = 'BTCUSDT'

        # order arguments
        #type='LIMIT'
        side = 'BUY'
        quantity = 0.002
        #price = 50000

        type='MARKET'



        # run for MARKET
        data =await futures_binance_new_order(type=type, symbol=symbol, side=side, quantity=quantity)
        order_price = float(data[0].get('avgPrice'))
        print(order_price)
        print(data)



        tp_type_limit = 'TAKE_PROFIT_PARTIAL_LIMIT'
        tp_type_market = 'TAKE_PROFIT_PARTIAL_MARKET'
        tp_side = 'SELL'
        take_profit_quantity = quantity
        #tp_price = 80000
        tp_price = round((order_price * 1.05), 1)
        tp_stop_price = tp_price

        stop_type = 'STOP_MARKET_FULL'
        stop_side = 'SELL'
        #stop_price = 50000
        stop_price = round((order_price * 0.95), 1)
        stop_closePosition = 'true'

        # run for limit
        #data = asyncio.run(futures_binance_new_order(type=type, symbol=symbol, side=side,
        #                                             quantity=quantity, price=price, timeInForce=timeInForce))
        #print(data)

    

        # run for take profit partial limit
        #tp_data = asyncio.run(futures_binance_new_order(tp_type_limit, symbol, tp_side, take_profit_quantity, tp_price, timeInForce, tp_stop_price))
        #print(tp_data)

        # run for take profit partial market
        task_tp  = asyncio.create_task(futures_binance_new_order(
            type=tp_type_market, symbol=symbol, side=tp_side, 
            quantity=take_profit_quantity, stop_price=tp_price, timeInForce=timeInForce,))
        #print(tp_data)


        # run for stop marketfull
        task_sl = asyncio.create_task(futures_binance_new_order(type=stop_type, symbol=symbol, stop_price=stop_price, 
                                                        side = stop_side, closePosition='true', timeInForce=timeInForce))
        


        tp_sl_result = await asyncio.gather(task_tp, task_sl)
        print(tp_sl_result)


    asyncio.run(main())