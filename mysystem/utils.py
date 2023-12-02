import numpy as np
import pandas as pd

def corr(x: pd.DataFrame, y: pd.DataFrame) -> pd.DataFrame:
    '''
    计算x和y在每个截面上相关系数的均值, x, y的index须相同 
    '''
    assert list(x.index) == list(y.index), 'x and y should have the same index'
    res = pd.Series(index = x.index)
    for date in x.index:
        res.loc[date] = x.loc[date].corr(y.loc[date])
    return res.mean()

def zscore(x: pd.DataFrame) -> pd.DataFrame:
    '''
    z-score标准化
    '''
    return ((x.T - x.mean(axis = 1)) / x.std(axis = 1)).T

def cleanOutlier(x: pd.DataFrame) -> pd.DataFrame:
    '''
    去极值, 将极值压缩到均值 +/- 5倍标准差
    '''
    y = x.copy()
    mean = x.mean(axis = 1)
    std = x.std(axis = 1)
    for date in y.index:
        y.loc[date, y.loc[date] > mean.loc[date] + 5 * std.loc[date]] = mean.loc[date] + 5 * std.loc[date]
        y.loc[date, y.loc[date] < mean.loc[date] - 5 * std.loc[date]] = mean.loc[date] - 5 * std.loc[date]
    return y