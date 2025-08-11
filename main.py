import time
import numpy as np
import pandas as pd
import get_kdj
import history_test
import get_bollinger_bands as bollinger
import matplotlib.pyplot as plt
from okx.api import Account
from okx.app import OkxSWAP
from okx.app.utils import eprint

# 永续合约行情不需要秘钥
account = Account(
flag = '0',
proxies = {},
proxy_host = None
)
sampling_count = 500 #采样数量
sampling_interval = 1 #秒
last_time = time.time() + sampling_interval

while True:

    #打印时间戳
    timestamp = time.time()
    local_time = time.localtime(timestamp)
    local_time_str = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    
    if(timestamp - last_time < sampling_interval):
        last_time = timestamp
        time.sleep(1)
        continue
    else:
        last_time = timestamp

    print(f"本地时间: {local_time_str}")

    # 获取1分钟KDJ
    kdj_1m = get_kdj.get_1m_kdj(account, sampling_count, n=9, m1=3, m2=3)
    # 获取15分钟KDJ
    kdj_15m = get_kdj.get_15m_kdj(account, sampling_count, n=9, m1=3, m2=3)
 
    # 计算布林带（默认Pandas方式）
    bollinger_band_15m = bollinger.calculate_bollinger_bands(kdj_15m, window=20, num_std=2)

    #判断买点
    buy_points = history_test.history_bolling_find_buy(bollinger_band_15m, kdj_15m, kdj_1m)
    sell_points = history_test.history_bolling_find_sell(bollinger_band_15m, kdj_15m, kdj_1m)

    # 获取账户信息
    balance_result = account.get_balance(ccy='USDT')
    # eprint(balance_result, length=20)

    # 可视化
    plt.figure(figsize=(12, 6))
    plt.plot(bollinger_band_15m.index, bollinger_band_15m['close'], label='Close Price', color='black')
    plt.plot(bollinger_band_15m['upper_band'], label='Upper Band', linestyle='--', color='red')
    plt.plot(bollinger_band_15m['middle_band'], label='Middle Band', color='blue')
    plt.plot(bollinger_band_15m['lower_band'], label='Lower Band', linestyle='--', color='green')
    plt.fill_between(bollinger_band_15m.index, bollinger_band_15m['upper_band'], bollinger_band_15m['lower_band'], alpha=0.1, color='grey')
    plt.title('GO1.0')
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.scatter(
        buy_points['time'],     # X轴：时间戳
        buy_points['price'],    # Y轴：价格
        s=50,                   # 点大小
        color='red',            # 填充色
        edgecolor='red',        # 边缘色
        marker='x',             # 星形标记
        alpha=0.9,              # 透明度
        zorder=10,              # 图层置顶
        label='buy'            # 图例标签
    )
    plt.scatter(
        sell_points['time'],    # X轴：时间戳
        sell_points['price'],   # Y轴：价格
        s=50,                   # 点大小
        color='green',          # 填充色
        edgecolor='green',      # 边缘色
        marker='x',             # 星形标记
        alpha=0.9,              # 透明度
        zorder=10,              # 图层置顶
        label='sell'            # 图例标签
    )
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
