import numpy as np
import pandas as pd

def corr(x: pd.DataFrame, y: pd.DataFrame, d: int) -> pd.DataFrame:
    '''
    计算x和y的d日相关系数, 即: \n
    '''
    return x.rolling(d).corr(y)