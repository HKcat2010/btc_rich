import time
import numpy as np
import pandas as pd
import get_kdj
import sys
import bs_boll_kdj
import logger
import get_bollinger_bands as bollinger
import matplotlib.pyplot as plt
from okx.api import Account
from okx.app import OkxSWAP
from okx.app.utils import eprint

def main(logger):

    account = Account(
        
        flag = '0',
        proxies = {},
        proxy_host = None
    )

    sampling_count = 200 #采样数量
    sampling_interval = 10 #秒
    last_time = time.time()

    while True:
        #打印时间戳
        timestamp = time.time()
        local_time = time.localtime(timestamp)
        local_time_str = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
        
        #logger.info(f"本地时间: {local_time_str} \n")

        if(timestamp <= last_time + sampling_interval ):
            time.sleep(1)
            continue
        else:
            last_time = timestamp

        try:
            # 获取1分钟KDJ
            kdj_1m = get_kdj.get_1m_kdj(account, sampling_count, n=9, m1=3, m2=3)
            # 获取15分钟KDJ
            kdj_15m = get_kdj.get_15m_kdj(account, sampling_count, n=9, m1=3, m2=3)
            logger.info(f"本地时间: {local_time_str} get kdj \n")

            # 计算布林带（默认Pandas方式）
            bollinger_band_15m = bollinger.calculate_bollinger_bands(kdj_15m, window=20, num_std=2)
            logger.info(f"本地时间: {local_time_str} calc bollinger \n")

            # 获取账户信息
            positions_result = account.get_positions(instType='SWAP')
            #eprint(positions_result, length=30)
            logger.info(f"本地时间: {local_time_str} get position \n")

        except Exception as e:
            logger.error(f"time: {local_time_str} err exit : {str(e)} \n")
            time.sleep(5) #5秒 后循环重试，必要时清仓
            sys.exit(e) #退出进程 由守护进程重新拉起

        # 没有持仓 判断买点
        if(positions_result['code'] == '0' or len(positions_result['data']) == 0):
            if(bs_boll_kdj.is_time_to_buy(logger, bollinger_band_15m, kdj_15m, kdj_1m)):
                #print(f"time: {local_time_str} buy price: {kdj_1m['close'][-1]} ")
                logger.info(f"buy time: {local_time_str} price: {kdj_1m['close'][-1]} \n")
        else:
            #有持仓 判断卖点
            if(bs_boll_kdj.is_time_to_sell(logger, bollinger_band_15m, kdj_15m, kdj_1m)):
                #print(f"time: {local_time_str} sell price: {kdj_1m['close'][-1]} ")
                logger.info(f"sell time: {local_time_str} price: {kdj_1m['close'][-1]} \n")

# 回测 买卖点
# 可视化
#'''
        buy_points = bs_boll_kdj.history_bolling_find_buy(bollinger_band_15m, kdj_15m, kdj_1m)
        sell_points = bs_boll_kdj.history_bolling_find_sell(bollinger_band_15m, kdj_15m, kdj_1m)
        
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

logger = logger.ImmediateDiskLogger(
    name = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())) + ".log",
    std_redirect=False
)
main(logger)
#'''