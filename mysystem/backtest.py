import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

import os
from typing import Optional
from .dataset import get_data

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class Backtest:
    def __init__(self, PATH: str, start: str, end: str, init_cap: float = 1e8, 
                 pool: str = 'all', output: list = ['ic', 'pnl', 'metrics']) -> None:
        self.STORE_PATH = os.path.join(PATH, '../alpha/')
        self.ret = get_data(PATH)['ret'].shift(-1)
        self.start = start
        self.end = end
        self.init_cap = init_cap
        self.pool = pool
        self.output = output


    def get_ic(self, alpha: pd.DataFrame) -> pd.DataFrame:
        ic = pd.DataFrame(index = alpha.index, columns = ['IC', 'rankIC'])
        for date in alpha.index:
            ic.loc[date, 'IC'] = alpha.loc[date].corr(self.ret.loc[date])
            ic.loc[date, 'rankIC'] = alpha.loc[date].corr(self.ret.loc[date], method = 'spearman')
        return ic        

    def plot_ic(self, ic: pd.Series, ALPHA_PATH: str, name: str) -> None:
        ic_mean = ic.mean(axis = 0).astype('float').round(4)
        icir = (ic.mean(axis = 0) / ic.std(axis = 0)).astype('float').round(4)
        plt.figure(figsize = (8, 4))
        plt.plot(ic.cumsum())
        plt.title(f'{name}_IC')
        plt.legend([f'IC mean = {ic_mean["IC"]} \nICIR = {icir["IC"]}', \
                    f'rankIC mean = {ic_mean["rankIC"]} \nrankICIR = {icir["rankIC"]}'])
        plt.xlabel('date')
        plt.ylabel('ic_cumsum', rotation = 0, labelpad = 10)
        plt.grid()
        plt.savefig(os.path.join(ALPHA_PATH, f'{name}_IC.jpg'))

    def get_weight(self, alpha: pd.DataFrame) -> pd.DataFrame:
        abssum = abs(alpha).sum(axis = 1)
        weight = (alpha.T / abssum[abssum > 1e-8]).T.fillna(0)
        return weight
    
    def get_pnl(self, weight: pd.DataFrame, init_cap) -> pd.Series:
        portfolio_ret = (weight * self.ret).sum(axis = 1).shift(1).fillna(0)
        pnl = init_cap * (1 + portfolio_ret.cumsum())
        return pnl
    
    def plot_pnl(self, pnl: pd.Series, ALPHA_PATH: str, name: str) -> None:
        ret = pnl.pct_change()
        ret_mean = (ret.mean().astype('float') * 252).round(4)
        sharpe_ratio = ((ret.mean() / ret.std()).astype('float') * np.sqrt(252)).round(4)
        plt.figure(figsize = (8, 4))
        plt.plot(pnl)
        plt.title(f'{name}_PnL')
        plt.legend([f'annually ret = {ret_mean} \nSharpe ratio = {sharpe_ratio}'])
        plt.xlabel('date')
        plt.ylabel('PnL', rotation = 0, labelpad = 10)
        plt.grid()
        plt.savefig(os.path.join(ALPHA_PATH, f'{name}_PnL.jpg'))

    def get_metrics(self, ic: pd.Series, pnl: pd.Series, ALPHA_PATH: str, name: str):
        ic_mean = ic.mean(axis = 0).astype('float').round(4)
        icir = (ic.mean(axis = 0) / ic.std(axis = 0)).astype('float').round(4)
        ret = pnl.pct_change()
        ret_mean = (ret.mean().astype('float') * 252).round(4)
        ret_std = (ret.std().astype('float') * np.sqrt(252)).round(4)
        sharpe_ratio = ((ret.mean() / ret.std()).astype('float') * np.sqrt(252)).round(4)
        winning_rate = (ret > 0).mean().astype('float').round(4)
        metrics = pd.DataFrame([ic_mean['IC'], icir['IC'], ic_mean['rankIC'], icir['rankIC'], 
                                ret_mean, ret_std, sharpe_ratio, winning_rate],
                                index = ['IC均值', 'ICIR', 'rankIC均值', 'rankICIR',
                                         '年化收益率', '年化波动率', '夏普比率', 
                                         '胜率'],
                                columns = [name.split('_')[0]])
        metrics.to_csv(os.path.join(ALPHA_PATH, f'{name}_metrics.csv'))
        display(metrics)


    def backtest(self, alpha: pd.DataFrame, alpha_name: str,
                 start: Optional[str] = None, end: Optional[str] = None, 
                 init_cap: Optional[float] = None, pool: Optional[str] = None, 
                 output: Optional[list] = None) -> None:
        if not os.path.exists(self.STORE_PATH):
            os.mkdir(self.STORE_PATH)
        ALPHA_PATH = os.path.join(self.STORE_PATH, alpha_name)
        if not os.path.exists(ALPHA_PATH):
            os.mkdir(ALPHA_PATH)

        if start is None:
            start = self.start
        if end is None:
            end = self.end
        if init_cap is None:
            init_cap = self.init_cap
        if pool is None:
            pool = self.pool
        if output is None:
            output = self.output

        alpha = alpha.shift(1)[start: end]
        name = f'{alpha_name}_{start}_{end}_{pool}'

        ic = self.get_ic(alpha)
        
        if 'ic' in output:
            ic.to_csv(os.path.join(ALPHA_PATH, f'{name}_IC.csv'))
            self.plot_ic(ic, ALPHA_PATH, name)
        
        if ic['IC'].mean() < 0:
            alpha = -alpha    

        weight = self.get_weight(alpha)
        if 'weight' in output:
            weight.to_csv(os.path.join(ALPHA_PATH, f'{name}_weight.csv'))
            
        pnl = self.get_pnl(weight, init_cap)
        pnl = pnl[start: end]
        if 'pnl' in output:
            pnl.to_csv(os.path.join(ALPHA_PATH, f'{name}_PnL.csv'))
            self.plot_pnl(pnl, ALPHA_PATH, name)

        if 'metrics' in output:
            self.get_metrics(ic, pnl, ALPHA_PATH, name)