from okx.app import OkxSWAP
from okx.app.utils import eprint
import pandas as pd
import time
import kdj

# 永续合约行情不需要秘钥
# 使用http和https代理，proxies={'http':'xxxxx','https:':'xxxxx'}，与requests中的proxies参数规则相同
# 转发：需搭建转发服务器，可参考：https://github.com/pyted/okx_resender
# okxSPOT.market 等同于 marketSPOT
def get_15m_kdj(account, len=50, n=9, m1=3, m2=3, instId='BTC-USDT-SWAP'):
    okxSWAP = OkxSWAP(
        key=account.key, secret=account.secret, passphrase=account.passphrase, 
        proxies=account.proxies, proxy_host=account.proxy_host
    )
    market = okxSWAP.market
    timestamp = time.time()
    local_time = time.localtime(timestamp)
    local_time_str = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    candle = market.update_history_candle(
        instId=instId,
        length=len,  # 保留数量
        end=local_time_str,  # end默认为本地计算机时间戳
        bar='15m',
    )['data']
    df = market.candle_to_df(candle)
    candle_arr = df.to_dict()
    kdj_data = pd.DataFrame({
        'ts': candle_arr['ts'],
        'high': candle_arr['h'],
        'low': candle_arr['l'],
        'close': candle_arr['c']
    })
    #pd.set_option('display.max_rows', None)  # 显示所有行
    #eprint(kdj_data)
    kdj_result = kdj.calculate_kdj(kdj_data, n, m1, m2)
    return kdj_result

def get_1m_kdj(account, len=50, n=9, m1=3, m2=3, instId='BTC-USDT-SWAP'):
    okxSWAP = OkxSWAP(
        key=account.key, secret=account.secret, passphrase=account.passphrase, 
        proxies=account.proxies, proxy_host=account.proxy_host
    )
    market = okxSWAP.market
    timestamp = time.time()
    local_time = time.localtime(timestamp)
    local_time_str = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    candle = market.update_history_candle(
        instId=instId,
        length=len,             # 保留数量
        end=local_time_str,     # end默认为本地计算机时间戳
        bar='1m',
    )['data']
    df = market.candle_to_df(candle)
    candle_arr = df.to_dict()
    kdj_data = pd.DataFrame({
        'ts': candle_arr['ts'],
        'high': candle_arr['h'],
        'low': candle_arr['l'],
        'close': candle_arr['c']
    })
    kdj_result = kdj.calculate_kdj(kdj_data, n, m1, m2)
    return kdj_result