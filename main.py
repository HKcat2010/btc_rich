import time
import numpy as np
import pandas as pd
import get_kdj
import bs_boll_kdj
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
sampling_interval = 15 #秒
last_time = time.time() + sampling_interval
log_file = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ".bs.log"
with open(log_file, 'a', encoding='utf-8') as log_file:

    while True:
        #打印时间戳
        timestamp = time.time()
        local_time = time.localtime(timestamp)
        local_time_str = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
        
        if(timestamp - last_time < sampling_interval):
            time.sleep(1)
            continue
        else:
            last_time = timestamp

        print(f"本地时间: {local_time_str}")

        try:
            # 获取1分钟KDJ
            kdj_1m = get_kdj.get_1m_kdj(account, instId='BTC-USDT', sampling_count, n=9, m1=3, m2=3)
            # 获取15分钟KDJ
            kdj_15m = get_kdj.get_15m_kdj(account, instId='BTC-USDT', sampling_count, n=9, m1=3, m2=3)
        
            # 计算布林带（默认Pandas方式）
            bollinger_band_15m = bollinger.calculate_bollinger_bands(kdj_15m, window=20, num_std=2)

            # 获取账户信息
            positions_result = account.get_positions(instType='SWAP')
            #eprint(positions_result, length=30)
        except okx.api._client.ResponseStatusError as e:
            print(f"time: {local_time_str} get data err: {str(e)} \n")
            log_file.write(f"time: {local_time_str} get data err: {str(e)} \n")
            time.sleep(5) #5秒 后循环重试，必要时清仓
            continue

        # 没有持仓 判断买点
        if(positions_result['code'] == '0' or len(positions_result['data']) == 0):
            if(bs_boll_kdj.is_time_to_buy(bollinger_band_15m, kdj_15m, kdj_1m)):
                print(f"time: {local_time_str} buy price: {kdj_1m['close'][-1]} ")
                log_file.write(f"buy time: {local_time_str} price: {kdj_1m['close'][-1]} \n")
        else:
            #有持仓 判断卖点
            if(bs_boll_kdj.is_time_to_sell(bollinger_band_15m, kdj_15m, kdj_1m)):
                print(f"time: {local_time_str} sell price: {kdj_1m['close'][-1]} ")
                log_file.write(f"sell time: {local_time_str} price: {kdj_1m['close'][-1]} \n")

        # 回测 买卖点
        #buy_points = bs_boll_kdj.history_bolling_find_buy(bollinger_band_15m, kdj_15m, kdj_1m)
        #sell_points = bs_boll_kdj.history_bolling_find_sell(bollinger_band_15m, kdj_15m, kdj_1m)

        # 可视化
        '''
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
        '''
