# https://github.com/tulin-ilya/tsl_long.git

# конкретно данный скрипт проверяет значение переменной market_position, если она long, то проверяет,
# in_position, если не в позиции, то заходит в позицию, назначает стоп и цену активации трейлинг стопа,
# далее, после достижения текущей ценой цены активации трейлинг стопа, снимает базовый стоп передвигает стоп с отставанием от high
# если цена достигает значение базового стопа, до того как достигла цены активации трейлинга позиция закрывается и ждет открытия следующей свечи
# если позиция закрылась по трейлинг стопу, то также ждет открытия следующей свечи

# pip install websocket-client

import websocket
import json

ticker = 'btcusdt'
interval = '1m'
socket = f'wss://fstream.binance.com/ws/{ticker}@kline_{interval}'

market_position = 'long'        # значение присваивается через вебхук или встроеный индикатор {long, short, flat}
in_position = False             # состояние текущей позиции
sl_perc = 0.5                   # % базового стопа
tsl_perc = 0.1                  # % трейлинг стопа, на сколько он будет отставать от high или low 
tsl_init_perc = 0.1             # % при котором начинается трейлиг стоп

candle_list = []
open_list = []
high_list =[]
low_list = []
close_list = []
sl_long_list = []
tsl_long_init_price_list = []
entry_list = []

def on_message(ws, message):
    global in_position, candle_list, open_list, high_list, low_list, close_list, sl_long_list, tsl_long_init_price_list, entry_list
    json_message        = json.loads(message)
    candle              = json_message['k']
    open                = float(candle['o'])
    high                = float(candle['h'])
    low                 = float(candle['l'])
    close               = float(candle['c'])
    is_candle_closed    = candle['x']

    candle_list.append(is_candle_closed)
    open_list.append(open)
    high_list.append(high)
    low_list.append(low)
    close_list.append(close)

    if market_position == 'long':
        if in_position:
            
            tsl_init_condition = close_list[-1] >= tsl_long_init_price_list[-1]
            if tsl_init_condition:
                tsl_long = high_list[-1] - (high_list[-1] * (tsl_perc / 100))
                sl_long_list.append(tsl_long)
                
                sl_rewrite_condition = sl_long_list[-1] != sl_long_list[-2]
                if sl_rewrite_condition:
                    print(f'sl changed - {sl_long_list[-1]}','\n')

            if  close_list[-1] <= sl_long_list[-1]:
                in_position = False
                
                print('-----exit from position-----')
                print(f'exit price - {sl_long_list[-1]}', '\n')
        
        elif candle_list[-2]:
            entry_list.append(open)
            bsl_long = entry_list[-1] - (entry_list[-1] * (sl_perc / 100))
            sl_long_list.append(bsl_long)
            tsl_long_init_price = entry_list[-1] + (entry_list[-1] * (tsl_init_perc / 100))
            tsl_long_init_price_list.append(tsl_long_init_price)
            in_position = True

            print('-----entry in position-----')
            print(f'entry price ---- {entry_list[-1]}')
            print(f'sl ------------- {sl_long_list[-1]}')
            print(f'tsl init price - {tsl_long_init_price_list[-1]}', '\n')
    
def on_open(ws):
    print('Connection Opened', '\n')

def on_close(ws):
    print('Connection Closed', '\n')
    
ws = websocket.WebSocketApp(socket, on_open = on_open, on_message = on_message, on_close = on_close)

ws.run_forever()