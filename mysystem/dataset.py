import numpy as np
import pandas as pd

import os

def get_data(PATH: str) -> dict:
    '''
    预处理数据: 得到一个存储各字段数据的字典data, 其keys为字段名称(str) \n
    PATH: 存储数据的路径, 设置为本repo的路径 \n    
    data有两个特殊字段: data['date']和data['id'], 分别为shape = (T,)和shape = (N,)的np.ndarray, 
    表示数据的时间段和包含的股票ID \n
    data的一般字段, 是一个shape = (T, N)的np.ndarray, 表示keys对应的字段数据, 
    例如data['close']表示股票的收盘价数据 \n
    注: 本系统数据基于20200101-20221231的沪深全市场股票, 于是data['date']为20200101-20221231之间的所有交易日, 
    data['id']为这段时间沪深全市场股票代码
    '''
    # 读取原始股票日行情数据
    raw_data = pd.read_feather(os.path.join(PATH, '../data/stk_daily.feather'))
    raw_data = raw_data[raw_data['stk_id'].apply(lambda x: not x.endswith('BJ'))] # 去掉北交所股票
    raw_data = list(raw_data.groupby('stk_id'))

    # 读取停盘数据
    suspend = pd.read_csv(os.path.join(PATH, 'newdata/suspend.csv'), index_col = 0)
    suspend.index = pd.to_datetime(suspend.index)

    # 将股票累积复权因子拼接成index为日期，columns为股票代码的DataFrame
    cumadj = pd.concat([d[1].set_index('date')['cumadj'].rename(d[0]) for d in raw_data], axis = 1)

    # 创建data字典和date, id字段
    data = {'date': np.array(list(cumadj.index)), 'id': np.array(cumadj.columns)}

    # 创建Volume字段
    data['volume'] = pd.concat([d[1].set_index('date')['volume'].rename(d[0]) for d in raw_data], axis = 1)
    data['volume'] = data['volume'][data['volume'] > 1e-8] # 仅保留交易量>0的值   

    # 创建OHLC字段
    for item in ['open', 'high', 'low', 'close']:
        raw_item = pd.concat([d[1].set_index('date')[item].rename(d[0]) for d in raw_data], axis = 1)
        data[item] = (raw_item * cumadj)[suspend == 0][data['volume'] > 1e-8] # 复权, 并除去停牌和交易量为0的股票

    # 创建ret字段
    data['ret'] = data['close'].pct_change(fill_method = None)

    # 创建vwap字段
    amount = pd.concat([d[1].set_index('date')['amount'].rename(d[0]) for d in raw_data], axis = 1)
    data['vwap'] = (amount * cumadj)[suspend == 0] / data['volume'] # 复权, 并除去停牌和交易量为0的股票

    return data
    
        
    