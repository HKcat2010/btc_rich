from okx.app.utils import eprint
import pandas as pd
def history_bolling_find_buy(bollinger_band, kdj_15m, kdj_1m):
    # 查找历史数据的买点
    print("history_bolling_find_buy begin")
    time = []
    price = []
    for index in kdj_15m.index:
        if index < 20:
            continue
        # 15min K 上穿 布林带下轨
        if( float(bollinger_band['lower_band'][index-1]) > float(kdj_15m['low'][index-1])
        and float(bollinger_band['lower_band'][index-1]) <= float(kdj_15m['high'][index-1])
        and float(bollinger_band['lower_band'][index]) < float(kdj_15m['low'][index])
        and float(kdj_15m['J'][index] < 25.0)
        and float(kdj_15m['J'][index-1] < float(kdj_15m['J'][index]))       #J值转向
        and float(kdj_15m['low'][index-1]) < float(kdj_15m['low'][index])): #低点抬高
            time.append(kdj_15m['ts'][index])
            price.append(float(kdj_15m['close'][index]))
            print(f"{kdj_15m['ts'][index]}: 买入价格: {float(kdj_15m['close'][index])}")

    print("history_bolling_find_buy end")
    return pd.DataFrame({
        'time': time,
        'price': price
    })

def history_bolling_find_sell(bollinger_band, kdj_15m, kdj_1m):
    # 查找历史数据的卖点
    print("history_bolling_find_sell begin")
    time = []
    price = []
    for index in kdj_15m.index:
        if index < 20:
            continue
        # 15min K 下穿 布林带上轨
        if( float(bollinger_band['upper_band'][index-1]) < float(kdj_15m['high'][index-1])
        and float(bollinger_band['upper_band'][index-1]) >= float(kdj_15m['low'][index-1])
        and float(bollinger_band['upper_band'][index]) > float(kdj_15m['high'][index])
        and float(kdj_15m['J'][index] > 85.0) # J 超买
        and float(kdj_15m['J'][index-1]) > float(kdj_15m['J'][index]) #J值转向
        and float(kdj_15m['high'][index-1]) > float(kdj_15m['high'][index])): #高点下跌
            time.append(kdj_15m['ts'][index])
            price.append(float(kdj_15m['close'][index]))
            print(f"{kdj_15m['ts'][index]}: 卖出价格: {float(kdj_15m['close'][index])}")

    print("history_bolling_find_sell end")
    return pd.DataFrame({
        'time': time,
        'price': price
    })