import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

import os
from typing import Optional
from .utils import corr
from .backtest import Backtest

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class AlphaPool:
    def __init__(self, PATH: str, start: str, end: str, pool: str = 'all', 
                 output: list = ['ic', 'pnl', 'metrics']) -> None:
        self.STORE_PATH = os.path.join(PATH, '../alpha/')
        self.start = start
        self.end = end
        self.pool = pool
        self.output = output
        self.alpha_list = {}
        self.backtest = Backtest(PATH = PATH, start = start, end = end, 
                                 pool = pool, output = output)

    def add_from_path(self) -> None:
        for alpha_name in os.listdir(self.STORE_PATH):
            ALPHA_PATH = os.path.join(self.STORE_PATH, alpha_name)
            name = f'{alpha_name}_{self.start}_{self.end}_{self.pool}'
            if os.path.exists(os.path.join(ALPHA_PATH, f'{name}_alpha.csv')):
                assert os.path.exists(os.path.join(ALPHA_PATH, f'{name}_alpha.csv')), \
                    f"missing file: metrics of alpha ({name}) in alphapool"
                alpha = pd.read_csv(os.path.join(ALPHA_PATH, f'{name}_alpha.csv'), index_col = 0)
                metrics = pd.read_csv(os.path.join(ALPHA_PATH, f'{name}_metrics.csv'), index_col = 0).T
                self.alpha_list[alpha_name] = {'alpha': alpha, 'metrics': metrics, 'path': ALPHA_PATH}

    def add(self, alpha: pd.DataFrame, alpha_name: str) -> None:
        if not os.path.exists(self.STORE_PATH):
            os.mkdir(self.STORE_PATH)
        ALPHA_PATH = os.path.join(self.STORE_PATH, alpha_name)
        if not os.path.exists(ALPHA_PATH):
            os.mkdir(ALPHA_PATH)

        alpha = alpha.shift(1)[self.start: self.end]
        name = f'{alpha_name}_{self.start}_{self.end}_{self.pool}'

        # 计算alpha的指标
        if not os.path.exists(os.path.join(ALPHA_PATH, f'{name}_metrics.csv')):
            self.backtest.backtest(alpha, alpha_name, output = ['metrics'])
        
        metrics = pd.read_csv(os.path.join(ALPHA_PATH, f'{name}_metrics.csv'), index_col = 0).T

        self.alpha_list[alpha_name] = {'alpha': alpha, 'metrics': metrics, 'path': ALPHA_PATH}
        # 储存alpha
        alpha.to_csv(os.path.join(ALPHA_PATH, f'{name}_alpha.csv'))
        

    def eval(self, alpha: pd.DataFrame, alpha_name: str, sort_index: Optional[str] = None) -> None:
        if not os.path.exists(self.STORE_PATH):
            os.mkdir(self.STORE_PATH)
        ALPHA_PATH = os.path.join(self.STORE_PATH, alpha_name)
        if not os.path.exists(ALPHA_PATH):
            os.mkdir(ALPHA_PATH)

        alpha = alpha.shift(1)[self.start: self.end]
        name = f'{alpha_name}_{self.start}_{self.end}_{self.pool}'    
        # 计算alpha的指标
        if not os.path.exists(os.path.join(ALPHA_PATH, f'{name}_metrics.csv')):
            self.backtest.backtest(alpha, alpha_name, output = ['metrics'])

        metrics = pd.read_csv(os.path.join(ALPHA_PATH, f'{name}_metrics.csv'), index_col = 0).T
        metrics['相关系数'] = 1.0
        metrics_list = [metrics]

        for pooled_alpha in self.alpha_list.values(): 
            metrics = pooled_alpha['metrics']
            metrics['相关系数'] = corr(alpha, pooled_alpha['alpha'])
            metrics_list.append(metrics)

        metrics_list = pd.concat(metrics_list, axis = 0)
        if sort_index is not None:
            assert sort_index in metrics_list.columns, f'sort index should be in {metrics_list.columns}'
        display(metrics_list)

        plt.figure(figsize = (len(metrics_list), 1))
        ax = sns.heatmap(metrics_list[['相关系数']].rename(columns = {'相关系数': alpha_name}).T, 
                         cmap="YlGnBu", annot=True, linewidths=.5)
        plt.yticks(rotation = 0)
        plt.show()
        
    
