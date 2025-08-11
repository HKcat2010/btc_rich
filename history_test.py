from okx.app.utils import eprint
import pandas as pd
def history_bolling_find_buy(bollinger_band, kdj_15m, kdj_1m):
    # 这里可以实现历史数据的买点查找逻辑
    print("history_bolling_find_buy begin")
    time = []
    price = []
    for index in kdj_15m.index:
        if index < 20:
            continue
        # 15min K 上传 布林带下轨
        if( float(bollinger_band['lower_band'][index-1]) > float(kdj_15m['low'][index-1])
        and float(bollinger_band['lower_band'][index-1]) <= float(kdj_15m['high'][index-1])
        and float(bollinger_band['lower_band'][index]) < float(kdj_15m['low'][index])):
            time.append(kdj_15m['ts'][index])
            price.append(float(kdj_15m['close'][index]))
            print(f"{kdj_15m['ts'][index]}: 买入价格: {float(kdj_15m['close'][index])}")

    print("history_bolling_find_buy end")
    return pd.DataFrame({
        'time': time,
        'price': price
    })
    '''
    if(balance_result['lower_band'][-1] == kdj_15m['d'] and kdj_1m['j'] < 0 ):
        # 执行买入操作
        print("本地时间: {local_time_str} 满足买入条件 \n\
                        15分钟KDJ: {kdj_15m[k]} {kdj_15m[d]} {kdj_15m[j]}\n\
                        1分钟KDJ: {kdj_1m[k]} {kdj_1m[d]} {kdj_1m[j]}")
    '''
def history_bolling_find_sell(bollinger_band, kdj_15m, kdj_1m):
    # 这里可以实现历史数据的卖点查找逻辑
    print(f"bollinger_band -1: {bollinger_band['upper_band']}")
    return "aaa"