from okx.app.utils import eprint
import pandas as pd
import logger

def is_time_to_buy(logger, bollinger_band, kdj_15m, kdj_1m):
    match_15m = False
    logger.info(f" lb[-2] {float(bollinger_band['lower_band'].iat[-2])} lb[-1] {float(bollinger_band['lower_band'].iat[-1])} 15m lp[-2].low {kdj_15m['low'].iat[-2]} lp[-2].high {float(kdj_15m['high'].iat[-2])} lp[-1].low {float(kdj_15m['low'].iat[-1])}")

    #[index-1] = .iat[-2] [index] = .iat[-1]
    if( float(bollinger_band['lower_band'].iat[-2]) > float(kdj_15m['low'].iat[-2])
        and float(bollinger_band['lower_band'].iat[-1]) < float(kdj_15m['high'].iat[-1])
        and float(kdj_15m['J'].iat[-2]) < 10.0
        and float(kdj_15m['J'].iat[-2]) < float(kdj_15m['J'].iat[-1])       # J值 抬高
        and float(kdj_15m['high'].iat[-2]) < float(kdj_15m['high'].iat[-1])):# 高点 抬高
            match_15m = True

    if match_15m: #满足 15min 要求
        if( float(kdj_1m['J'].iat[-1]) < 10.0 ): #当前简单以 J<10 要求
            logger.critical(f"{kdj_1m['ts'].iat[-1]}: 买入价格: {float(kdj_1m['close'].iat[-1])}")
            return True

    return False

def is_time_to_sell(logger, bollinger_band, kdj_15m, kdj_1m):
    match_15m = False
    if( float(bollinger_band['upper_band'].iat[-2]) < float(kdj_15m['high'].iat[-2])
    and float(bollinger_band['upper_band'].iat[-2]) >= float(kdj_15m['low'].iat[-2])
    and float(bollinger_band['upper_band'].iat[-1]) > float(kdj_15m['high'].iat[-1])
    and float(kdj_15m['J'].iat[-1] > 85.0) # J 超买
    and float(kdj_15m['J'].iat[-2]) > float(kdj_15m['J'].iat[-1]) #J值转向
    and float(kdj_15m['high'].iat[-2]) > float(kdj_15m['high'].iat[-1])): #高点下跌
        match_15m = True
    
    if match_15m: #满足 15min 要求
        if( float(kdj_1m['J'].iat[-1]) > 90.0 ): #当前简单以 J>90 要求
            logger.critical(f"{kdj_1m['ts'].iat[-1]}: 卖出价格: {float(kdj_1m['close'].iat[-1])}")
            return True

    return False

def history_bolling_find_buy(bollinger_band, kdj_15m, kdj_1m):
    # 查找历史数据的买点
    print("history_bolling_find_buy begin")
    time = []
    price = []
    for index in kdj_15m.index:
        if index < 20:
            continue
        # 15min K 上穿 布林带下轨
        '''
        if( float(bollinger_band['lower_band'][index-1]) > float(kdj_15m['low'][index-1])
        and float(bollinger_band['lower_band'][index-1]) <= float(kdj_15m['high'][index-1])
        and float(bollinger_band['lower_band'][index]) < float(kdj_15m['low'][index])
        and float(kdj_15m['J'][index] < 25.0)
        and float(kdj_15m['J'][index-1] < float(kdj_15m['J'][index]))       #J值转向
        and float(kdj_15m['low'][index-1]) < float(kdj_15m['low'][index])): #低点抬高
        '''
        if( float(bollinger_band['lower_band'][index-1]) > float(kdj_15m['low'][index-1])
        and float(bollinger_band['lower_band'][index]) < float(kdj_15m['high'][index])
        and float(kdj_15m['J'][index-1]) < 10.0
        and float(kdj_15m['J'][index-1]) < float(kdj_15m['J'][index])       # J值 抬高
        and float(kdj_15m['high'][index-1]) < float(kdj_15m['high'][index])):# 高点 抬高
            time.append(kdj_15m['ts'][index])
            price.append(float(kdj_15m['close'][index]))
            print(f"{kdj_15m['ts'][index]}: 买入价格: {float(kdj_15m['close'][index])}")

        '''
        if(float(kdj_15m['close'][index]) == 117221.6):
            print(f"""{kdj_15m['ts'][index]}:
                lower_band[-1]:{float(bollinger_band['lower_band'][index-1])}  low[-1]:{float(kdj_15m['low'][index-1])} 
                lower_band:{float(bollinger_band['lower_band'][index])} high:{float(kdj_15m['high'][index])} 
                kdj_15m['J'][-1]:{float(kdj_15m['J'][index-1])} kdj_15m['J']:{float(kdj_15m['J'][index])} 
                high[-1]: {float(kdj_15m['high'][index-1])} high:{float(kdj_15m['high'][index])}
                """)
        '''
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