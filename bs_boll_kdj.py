from okx.app.utils import eprint
import pandas as pd
import matplotlib.pyplot as plt
import logger
import mplcursors
import bisect

over_sell_J = 30.0
over_buy_J = 70.0

def history_find_bs_range(logger, kdj_long, begin, init_label = "over_sell"):
    time = []
    ts_ms = []
    price = []
    label = []
    J_avg = []
    bg_idx = bisect.bisect_right(kdj_long['ts_ms'], begin)
    smooth_wind=7
    last_label = init_label
    #kdj_long_K_avg = kdj_long['K'].rolling(window=smooth_wind).mean()
    kdj_long_J_avg = kdj_long['J'].rolling(window=smooth_wind).mean()
    #print(f" 4h begin ts {kdj_long['ts'][bg_idx]} ts_ms {kdj_long['ts_ms'][bg_idx]} J {kdj_long['J'].iat[bg_idx]}")

    for index in range(bg_idx, kdj_long.shape[0], 1):
        '''
        # 金叉 在4H 粒度上 会浪费最猛的 第一波，所以用激进 一点的 J转向判断
        if( kdj_long_K_avg.iat[index-2] < kdj_long_J_avg.iat[index-1]
        and kdj_long_J_avg.iat[index-1] <= kdj_long_K_avg.iat[index]
        and last_label != "buy"):# 金叉
        '''
        if( kdj_long_J_avg.iat[index-1] <= kdj_long_J_avg.iat[index]
        and kdj_long_J_avg.iat[index-1] <= over_sell_J
        and kdj_long_J_avg.iat[index] > over_sell_J #J脱离超卖区
        and last_label != "buy" ):
            time.append(kdj_long['ts'].iat[index])
            ts_ms.append(kdj_long['ts_ms'].iat[index])
            price.append(float(kdj_long['close'].iat[index]))
            label.append("buy")
            last_label = "buy"
            J_avg.append(kdj_long_J_avg.iat[index])
            logger.info(f"{kdj_long['ts'].iat[index]}: buy range begin J {kdj_long['J'].iat[index]}")
        elif( kdj_long_J_avg.iat[index-1] >= kdj_long_J_avg.iat[index]
        and kdj_long_J_avg.iat[index-1] >= over_buy_J #进入超买
        and last_label != "high_wave"):
            time.append(kdj_long['ts'].iat[index])
            ts_ms.append(kdj_long['ts_ms'].iat[index])
            price.append(float(kdj_long['close'].iat[index]))
            label.append("high_wave")
            last_label = "high_wave"
            J_avg.append(kdj_long_J_avg.iat[index])
            logger.info(f"{kdj_long['ts'].iat[index]}: high_wave range begin J {kdj_long['J'].iat[index]}")
        elif( kdj_long_J_avg.iat[index-1] > kdj_long_J_avg.iat[index]
        and kdj_long_J_avg.iat[index-1] >= over_buy_J
        and kdj_long_J_avg.iat[index] < over_buy_J 
        and last_label != "sell"):
            time.append(kdj_long['ts'].iat[index])
            ts_ms.append(kdj_long['ts_ms'].iat[index])
            price.append(float(kdj_long['close'].iat[index]))
            label.append("sell")
            last_label = "sell"
            J_avg.append(kdj_long_J_avg.iat[index])
            logger.info(f"{kdj_long['ts'].iat[index]}: sell range begin J {kdj_long['J'].iat[index]}")
        elif( kdj_long_J_avg.iat[index-1] < kdj_long_J_avg.iat[index]
        and kdj_long_J_avg.iat[index-1] < over_sell_J 
        and last_label != "low_wave"):
            time.append(kdj_long['ts'].iat[index])
            ts_ms.append(kdj_long['ts_ms'].iat[index])
            price.append(float(kdj_long['close'].iat[index]))
            label.append("low_wave")
            last_label = "low_wave"
            J_avg.append(kdj_long_J_avg.iat[index])
            logger.info(f"{kdj_long['ts'].iat[index]}: low_wave range begin J {kdj_long['J'].iat[index]}")

    bs_range = pd.DataFrame({
        'time': time,
        'ts_ms': ts_ms,
        'price': price,
        'label': label,
        'J_avg': J_avg
    })
    '''
    plt.figure(figsize=(12, 6))
    plt.plot(kdj_long['ts'], kdj_long['K'], label='K_avg', color='red')
    plt.plot(kdj_long['ts'], kdj_long['J'], label='J_avg', linestyle='--', color='green')
    plt.title('KDJ_avg')
    plt.xlabel('Timestamp')
    plt.ylabel('KDJ')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.scatter(
        bs_range[bs_range['label']=="buy"]['time'],
        bs_range[bs_range['label']=="buy"]['J_avg'],
        s=60,  # 增大点的大小
        color='red', 
        edgecolors='red',
        zorder=3,  # 确保点在最上层
        label='关键J值点'
    )
    plt.scatter(
        bs_range[bs_range['label']=="sell"]['time'],
        bs_range[bs_range['label']=="sell"]['J_avg'],
        s=60,  # 增大点的大小
        color='green', 
        edgecolors='green',
        zorder=3,  # 确保点在最上层
        label='关键J值点'
    )
    cursor = mplcursors.cursor(plt.gca().collections[0])
    cursor.connect("add", lambda sel: sel.annotation.set_text(f"时间: {sel.target[0]:%Y-%m-%d %H:%M}\nJ值: {sel.target[1]:.2f}"))
    plt.show()
    '''
    logger.info(f"check buy or sell range end")
    return bs_range

def is_time_to_buy(logger, bollinger_band, kdj_15m, kdj_1m):
    #检查15m kdj 是否满足卖点
    if( float(bollinger_band['lower_band'].iat[-2]) > float(kdj_15m['low'].iat[-2])
        and float(bollinger_band['lower_band'].iat[-1]) < float(kdj_15m['high'].iat[-1])
        and float(kdj_15m['J'].iat[-2]) < float(kdj_15m['J'].iat[-1])           # J值 抬高
        and float(kdj_15m['high'].iat[-2]) < float(kdj_15m['high'].iat[-1]) ):   # 高点 抬高
            logger.info(f"""{kdj_15m['ts'].iat[-1]}:
                lower_band[-2]:{float(bollinger_band['lower_band'].iat[-2])}  low[-2]:{float(kdj_15m['low'].iat[-2])} 
                lower_band[-1]:{float(bollinger_band['lower_band'].iat[-1])} high[-1]:{float(kdj_15m['high'].iat[-1])} 
                kdj_15m['J'].iat[-2]:{float(kdj_15m['J'].iat[-2])} kdj_15m['J'].iat[-1]:{float(kdj_15m['J'].iat[-1])} 
                high[-2]: {float(kdj_15m['high'].iat[-2])}
                """)
    else:
        return False

    #检查1m kdj 是否满足买点
    if( float(kdj_1m['J'].iat[-1]) < 10.0 ):
        logger.critical(f"{kdj_1m['ts'].iat[-1]}: buy price: {float(kdj_1m['close'].iat[-1])}")
        return True

    return False

def is_time_to_sell(logger, bollinger_band, kdj_15m, kdj_1m):
    #检查15m kdj 是否满足卖点
    if( float(bollinger_band['upper_band'].iat[-2]) < float(kdj_15m['high'].iat[-2])
    and float(bollinger_band['upper_band'].iat[-2]) >= float(kdj_15m['low'].iat[-2])
    and float(bollinger_band['upper_band'].iat[-1]) > float(kdj_15m['high'].iat[-1])
    and float(kdj_15m['J'].iat[-1] > 85.0) # J 超买
    and float(kdj_15m['J'].iat[-2]) > float(kdj_15m['J'].iat[-1]) #J值转向
    and float(kdj_15m['low'].iat[-2]) > float(kdj_15m['low'].iat[-1])): #低点下跌
        #满足 15min 要求
        logger.info(f"""{kdj_15m['ts'].iat[-1]}:
                upper_band[-2]:{float(bollinger_band['upper_band'].iat[-2])}  high[-2]:{float(kdj_15m['high'].iat[-2])} 
                upper_band[-1]:{float(bollinger_band['upper_band'].iat[-1])} high[-1]:{float(kdj_15m['high'].iat[-1])} 
                kdj_15m['J'].iat[-2]:{float(kdj_15m['J'].iat[-2])} kdj_15m['J'].iat[-1]:{float(kdj_15m['J'].iat[-1])} 
                low[-2]: {float(kdj_15m['low'].iat[-2])}
                """)
    else:
        return False
    
    #检查1m kdj 是否满足卖点
    if( float(kdj_1m['J'].iat[-1]) > 90.0 ): #当前简单以 J>90 要求
        logger.critical(f"{kdj_1m['ts'].iat[-1]}: 卖出价格: {float(kdj_1m['close'].iat[-1])}")
        return True

    return False

def history_bolling_find_buy(bollinger_band, kdj_15m, kdj_1m):
    # 查找历史数据的买点
    print("history_bolling_find_buy begin")
    time = []
    price = []
    for index in range(20, kdj_15m.shape[0], 1):
        # 15min K 上穿 布林带下轨
        if( float(bollinger_band['lower_band'].iat[index-1]) > float(kdj_15m['low'].iat[index-1])
        and float(bollinger_band['lower_band'].iat[index]) < float(kdj_15m['high'].iat[index])
        and float(kdj_15m['J'].iat[index-1]) < 25.0
        and float(kdj_15m['J'].iat[index-1]) < float(kdj_15m['J'].iat[index])       # J值 抬高
        and float(kdj_15m['high'].iat[index-1]) < float(kdj_15m['high'].iat[index])):# 高点 抬高
            time.append(kdj_15m['ts'].iat[index])
            price.append(float(kdj_15m['close'].iat[index]))
            print(f"{kdj_15m['ts'].iat[index]}: buy price: {float(kdj_15m['close'].iat[index])}")

        '''
        if(float(kdj_15m['close'].iat[index]) == 117221.6):
            print(f"""{kdj_15m['ts'].iat[index]}:
                lower_band[-1]:{float(bollinger_band['lower_band'].iat[index-1])}  low[-1]:{float(kdj_15m['low'].iat[index-1])} 
                lower_band:{float(bollinger_band['lower_band'].iat[index])} high:{float(kdj_15m['high'].iat[index])} 
                kdj_15m['J'].iat[-1]:{float(kdj_15m['J'].iat[index-1])} kdj_15m['J']:{float(kdj_15m['J'].iat[index])} 
                high[-1]: {float(kdj_15m['high'].iat[index-1])} high:{float(kdj_15m['high'].iat[index])}
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
    for index in range(20, kdj_15m.shape[0], 1):
        # 15min K 下穿 布林带上轨
        if( float(bollinger_band['upper_band'].iat[index-1]) < float(kdj_15m['high'].iat[index-1])
        and float(bollinger_band['upper_band'].iat[index-1]) >= float(kdj_15m['low'].iat[index-1])
        and float(bollinger_band['upper_band'].iat[index]) > float(kdj_15m['high'].iat[index])
        and float(kdj_15m['J'].iat[index] > 85.0) # J 超买
        and float(kdj_15m['J'].iat[index-1]) > float(kdj_15m['J'].iat[index]) #J值转向
        and float(kdj_15m['high'].iat[index-1]) > float(kdj_15m['high'].iat[index])): #高点下跌
            time.append(kdj_15m['ts'].iat[index])
            price.append(float(kdj_15m['close'].iat[index]))
            print(f"{kdj_15m['ts'].iat[index]}: 卖出价格: {float(kdj_15m['close'].iat[index])}")

    print("history_bolling_find_sell end")
    return pd.DataFrame({
        'time': time,
        'price': price
    })