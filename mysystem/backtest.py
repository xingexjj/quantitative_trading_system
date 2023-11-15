import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Backtest:
    def __init__(self, ret: pd.DataFrame) -> None:
        self.ret = ret

    def backtest(self, alpha, start, end, init_cap = 1e8, pool = 'all', ic = True, pnl = True):
        alpha = alpha.shift(1)
        weight = self.get_weight(alpha)

    def get_weight(self, alpha: pd.DataFrame) -> pd.DataFrame:
        return alpha / np.nansum(abs(alpha))
    
    def get_ic(self, alpha: pd.DataFrame):
        return 