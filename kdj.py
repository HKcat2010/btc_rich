import pandas as pd

def calculate_kdj(data, n=9, m1=3, m2=3):
    """
    计算 KDJ 指标 (默认参数 9,3,3)
    :param data: DataFrame，需包含列 ['high', 'low', 'close']
    :param n: RSV 计算周期 (默认9)
    :param m1: K 值平滑周期 (默认3)
    :param m2: D 值平滑周期 (默认3)
    :return: 添加了 K, D, J 列的 DataFrame
    """
    # 计算 N 日最低价和最高价
    low_min = data['low'].rolling(window=n, min_periods=1).min()
    high_max = data['high'].rolling(window=n, min_periods=1).max()
    
    # 计算 RSV = (收盘价 - N日最低价) / (N日最高价 - N日最低价) * 100
    rsv = (data['close'] - low_min) / (high_max - low_min) * 100
    rsv = rsv.fillna(50)  # 处理初始 NaN 值
    
    # 初始化 K, D, J 序列
    k = pd.Series(0.0, index=data.index)
    d = pd.Series(0.0, index=data.index)
    
    # 计算 K 值（RSV 的 m1 日指数平滑）
    k = rsv.ewm(alpha=1/m1, adjust=False).mean()
    
    # 计算 D 值（K 值的 m2 日指数平滑）
    d = k.ewm(alpha=1/m2, adjust=False).mean()
    
    # 计算 J 值 = 3K - 2D
    j = 3 * k - 2 * d
    
    # 将结果添加到 DataFrame
    data['K'] = k
    data['D'] = d
    data['J'] = j
    
    return data

# ====================== 使用示例 ======================
#if __name__ == "__main__":
#    # 示例数据（需替换为实际数据）
#    data = pd.DataFrame({
#        'high': [50, 52, 53, 55, 54, 56, 57, 58, 59, 60],
#        'low': [48, 49, 50, 51, 52, 53, 54, 55, 56, 57],
#        'close': [49, 51, 52, 54, 53, 55, 56, 57, 58, 59]
#    })
#    
#    # 计算 KDJ
#    result = calculate_kdj(data.copy(), n=9, m1=3, m2=3)
#    
#    # 打印结果
#    print(result[['close', 'K', 'D', 'J']].tail())