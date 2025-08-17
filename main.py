import time
import get_kdj
import sys
import bs_boll_kdj
import logger
import get_bollinger_bands as bollinger
import matplotlib.pyplot as plt
from okx.api import Account

def main(logger):

    account = Account(
        
        flag = '0',
        proxies = {},
        proxy_host = None
    )

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
            kdj_1m = get_kdj.get_kdj_data(logger, account, 1000, n=9, m1=3, m2=3, bar="1m")
            # 获取15分钟KDJ
            kdj_15m = get_kdj.get_kdj_data(logger, account, 1000, n=9, m1=3, m2=3, bar="15m")
            # 获取4小时KDJ 判断方向50根K 理论上足以
            kdj_long = get_kdj.get_kdj_data(logger, account, 500, n=9, m1=3, m2=3, bar="4H")
            #logger.info(f"本地时间: {local_time_str} get kdj \n")

            # 计算布林带（默认Pandas方式）
            bollinger_band_15m = bollinger.calculate_bollinger_bands(kdj_15m, window=20, num_std=2)
            #logger.info(f"本地时间: {local_time_str} calc bollinger \n")

            # 获取账户信息
            positions_result = account.get_positions(instType='SWAP')
            #logger.info(f"本地时间: {local_time_str} get position \n")

        except Exception as e:
            logger.error(f"time: {local_time_str} err exit : {str(e)} \n")
            time.sleep(5) #5秒 后循环重试，必要时清仓
            sys.exit(e) #退出进程 由守护进程重新拉起
        
        # 判定区间
        print(f" 15 min begin ts_ms {kdj_15m['ts_ms'][0]} ts {kdj_15m['ts'][0]}")
        bs_range = bs_boll_kdj.history_find_bs_range(logger, kdj_long, begin=kdj_15m['ts_ms'][0])
        
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
        plt.plot(bollinger_band_15m['ts'], bollinger_band_15m['close'], label='Close Price', color='black')
        plt.plot(bollinger_band_15m['ts'], bollinger_band_15m['upper_band'], label='Upper Band', linestyle='--', color='red')
        plt.plot(bollinger_band_15m['ts'], bollinger_band_15m['middle_band'], label='Middle Band', color='blue')
        plt.plot(bollinger_band_15m['ts'], bollinger_band_15m['lower_band'], label='Lower Band', linestyle='--', color='green')
        plt.fill_between(bollinger_band_15m['ts'], bollinger_band_15m['upper_band'], bollinger_band_15m['lower_band'], alpha=0.1, color='grey')
        plt.title('GO1.0')
        plt.xlabel('Timestamp')
        plt.ylabel('Price')
        plt.scatter(
            buy_points['time'],     # X轴：时间戳
            buy_points['price'],    # Y轴：价格
            s=50,                   # 点大小
            color='red',            # 填充色
            marker='x',             # 星形标记
            alpha=0.9,              # 透明度
            zorder=10,              # 图层置顶
            label='buy'             # 图例标签
        )
        plt.scatter(
            sell_points['time'],    # X轴：时间戳
            sell_points['price'],   # Y轴：价格
            s=50,                   # 点大小
            color='green',          # 填充色
            marker='x',             # 星形标记
            alpha=0.9,              # 透明度
            zorder=10,              # 图层置顶
            label='sell'            # 图例标签
        )
        # 填充 看多 红色 看空 绿色
        for idx in range(0, bs_range.shape[0], 1):
            
            print(f"{idx} {bs_range['time'].iat[idx]}  {bs_range['label'].iat[idx]} ")
            if(idx < bs_range.shape[0] - 1):
                color_end = bs_range['time'].iat[idx+1]
            else:
                color_end = bollinger_band_15m['ts'].iat[-1] # 最后一个区域

            if(bs_range['label'].iat[idx]=="buy"):    
                plt.axvspan(bs_range['time'].iat[idx], color_end, alpha=0.2, color='red', label='buy')
            elif(bs_range['label'].iat[idx]=="high_wave"):
                plt.axvspan(bs_range['time'].iat[idx], color_end, alpha=0.2, color='yellow', label='high_wave')
            elif(bs_range['label'].iat[idx]=="sell"):
                plt.axvspan(bs_range['time'].iat[idx], color_end, alpha=0.2, color='green', label='sell')
            elif(bs_range['label'].iat[idx]=="low_wave"):
                plt.axvspan(bs_range['time'].iat[idx], color_end, alpha=0.2, color='blue', label='low_wave')
        '''
        plt.scatter(
            bs_range[bs_range['label']=="buy"]['time'],     # X轴：时间戳
            bs_range[bs_range['label']=="buy"]['price'],    # Y轴：价格
            s=60,                   # 增大点的大小
            color='red', 
            edgecolors='red',
            marker='o',             # 标记
            zorder=10,              # 确保点在最上层
            label='buy_range'
        )
        plt.scatter(
            bs_range[bs_range['label']=="sell"]['time'],    # X轴：时间戳
            bs_range[bs_range['label']=="sell"]['price'],   # Y轴：价格
            s=60,                   # 增大点的大小
            color='green', 
            edgecolors='green',
            marker='o',             # 标记
            zorder=10,              # 确保点在最上层
            label='sell_range'
        )
        '''
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