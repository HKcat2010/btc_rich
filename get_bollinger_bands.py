import pandas as pd

def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    计算布林带指标（上轨、中轨、下轨）
    
    参数:
        data (pd.DataFrame): 必须包含 'close' 和 'ts' 列
        window (int): 移动平均周期，默认 20
        num_std (float): 标准差倍数，默认 2
    
    返回:
        pd.DataFrame: 新增三列 ['upper_band', 'middle_band', 'lower_band']
    """
    # 1. 数据校验
    if 'close' not in data.columns or 'ts' not in data.columns:
        raise ValueError("输入DataFrame必须包含 'close' 和 'ts' 列")

    # 2. 确保时间戳为索引（便于绘图）
    df = data.copy()
    if df.index.name != 'ts':
        df = df.set_index('ts')

    # 3. 计算布林带
    df['middle_band'] = df['close'].rolling(window=window).mean()
    rolling_std = df['close'].rolling(window=window).std(ddof=0)  # 对齐TA-Lib用总体标准差
    df['upper_band'] = df['middle_band'] + (num_std * rolling_std)
    df['lower_band'] = df['middle_band'] - (num_std * rolling_std)

    return df