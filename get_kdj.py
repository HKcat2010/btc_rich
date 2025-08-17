from okx.app import OkxSWAP
import pandas as pd
import logger
import time
import kdj

# 永续合约行情不需要秘钥
# 使用http和https代理，proxies={'http':'xxxxx','https:':'xxxxx'}，与requests中的proxies参数规则相同
# 转发：需搭建转发服务器，可参考：https://github.com/pyted/okx_resender
# okxSPOT.market 等同于 marketSPOT
def get_kdj_data(logger, account, len=50, n=9, m1=3, m2=3, bar="1m", instId='BTC-USDT-SWAP'):
    okxSWAP = OkxSWAP(
        key=account.key, secret=account.secret, passphrase=account.passphrase, 
        proxies=account.proxies, proxy_host=account.proxy_host
    )

    timestamp = time.time()
    local_time = time.localtime(timestamp)
    local_time_str = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    market = okxSWAP.market
    candle = market.update_history_candle(
        instId=instId,
        length=len,  # 保留数量
        end=local_time_str,  # end默认为本地计算机时间戳
        bar=bar
    )
    if (candle['code'] != '0' and candle['code'] != 'CANDLE_END_ERROR'):
        logger.error(f"update_history_candle err {candle}")
        raise ValueError("update_history_candle err")
    df = market.candle_to_df(candle['data'])
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