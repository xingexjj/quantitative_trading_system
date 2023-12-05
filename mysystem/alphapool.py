import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display # 展示pd.DataFrame的函数

import os
from typing import Optional
from .utils import corr
from .backtest import Backtest

# 设置plt负号和中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class AlphaPool:
    '''
    因子池
    PATH: 存储因子数据的路径, 设置为本repo的路径 \n
    start: 因子池开始的时间, 例如'20200101' \n
    end: 因子池结束的时间, 例如'20221231' \n
    pool: 资产池, 目前支持的可选项有'all'(沪深全市场), 'hs300'(沪深300成分股, 实时跟踪),
    也可直接传入一个one-hot的pd.DataFrame \n
    output: 因子回测的输出, 可选项包括ic, pnl, weight, metrics
    '''
    def __init__(self, PATH: str, start: str, end: str, pool = 'all', 
                 output: list = ['ic', 'pnl', 'metrics']) -> None:
        self.STORE_PATH = os.path.join(PATH, '../alpha/') # 储存因子的路径
        self.start = start
        self.end = end
        self.pool_name, self.pool = self.get_pool(pool)
        self.output = output
        self.alpha_list = {}
        self.backtest = Backtest(PATH = PATH, start = start, end = end, 
                                 pool = pool, output = output) # 用于回测因子池中因子的回测类

    def get_pool(self, pool) -> Optional[pd.DataFrame]:
        '''
        获取股票池的DataFrame
        '''
        # 检查pool输入格式
        assert isinstance(pool, (str, pd.DataFrame)), 'pool should be str type or pd.DataFrame'
        if isinstance(pool, str):
            # 沪深全股票
            if pool == 'all':
                return 'all', None
            # 沪深300
            elif pool == 'hs300':
                pool = pd.read_csv(os.path.join(self.PATH, 'newdata/hs300.csv'), index_col = 0)
                pool.index = pd.to_datetime(pool.index)
                return 'hs300', pool
            # 不支持的字符串, 默认为all
            else:
                print(f"unsupported pool {pool}, setting pool to 'all'")
                return 'all', None
        
        else: # 自定义股票池, 需保证日期和股票名均在可回测范围内
            assert pool.index.isin(self.ret.index).all(), 'invalid date'
            assert pool.columns.isin(self.ret.columns).all(), 'invalid stock name'
            return pool.index.name, pool

    def add_from_path(self) -> None:
        '''
        从因子池路径调取已经存在的因子
        '''
        for alpha_name in os.listdir(self.STORE_PATH): # 找到所有因子
            ALPHA_PATH = os.path.join(self.STORE_PATH, alpha_name)
            # 若因子不在因子池中, 则加入
            if alpha_name not in self.alpha_list.keys():
                name = f'{alpha_name}_{self.start}_{self.end}_{self.pool_name}'
                if os.path.exists(os.path.join(ALPHA_PATH, f'{name}_alpha.csv')):
                    assert os.path.exists(os.path.join(ALPHA_PATH, f'{name}_metrics.csv')), \
                        f"missing file: metrics of alpha ({name}) in alphapool" # 检查因子回测文件存在
                    alpha = pd.read_csv(os.path.join(ALPHA_PATH, f'{name}_alpha.csv'), index_col = 0) # 因子值
                    metrics = pd.read_csv(os.path.join(ALPHA_PATH, f'{name}_metrics.csv'), index_col = 0).T # 因子回测指标
                    self.alpha_list[alpha_name] = {'alpha': alpha, 'metrics': metrics, 'path': ALPHA_PATH}
        print(f'Successfully add alphas from {self.STORE_PATH}')

    def add(self, alpha: pd.DataFrame, alpha_name: str) -> None:
        '''
        向因子池加入因子
        alpha: 需要加入的因子
        alpha_name: 因子名称
        '''
        # 检查, 创建储存因子的路径
        if not os.path.exists(self.STORE_PATH):
            os.mkdir(self.STORE_PATH)
        ALPHA_PATH = os.path.join(self.STORE_PATH, alpha_name)
        if not os.path.exists(ALPHA_PATH):
            os.mkdir(ALPHA_PATH)

        if self.pool is not None:
            alpha = alpha[self.pool == 1] # 资产池内股票的因子值
        alpha = alpha.shift(1)[self.start: self.end] # 回测期间内股票的因子值
        name = f'{alpha_name}_{self.start}_{self.end}_{self.pool_name}'

        # 计算alpha的回测指标
        if not os.path.exists(os.path.join(ALPHA_PATH, f'{name}_metrics.csv')):
            self.backtest.backtest(alpha, alpha_name, output = ['metrics'])
        
        metrics = pd.read_csv(os.path.join(ALPHA_PATH, f'{name}_metrics.csv'), index_col = 0).T

        self.alpha_list[alpha_name] = {'alpha': alpha, 'metrics': metrics, 'path': ALPHA_PATH}
        # 储存alpha
        alpha.to_csv(os.path.join(ALPHA_PATH, f'{name}_alpha.csv'))
        print(f'Successfully add alpha {alpha_name} to {ALPHA_PATH}')
        

    def eval(self, alpha: pd.DataFrame, alpha_name: str, sort_index: Optional[str] = None) -> None:
        '''
        计算因子alpha与因子池中因子的相关系数, 并对比alpha与因子池中因子的回测指标
        alpha: 需要评估的新因子
        alpha_name: 因子名称
        sort_index: 回测指标排序方式,可选项有IC均值, ICIR, rankIC均值, rankICIR, 年化收益率, 年化波动率, 
        夏普比率, 胜率, 相关系数, 若为None则不排序
        '''
        # 检查, 创建储存因子的路径
        if not os.path.exists(self.STORE_PATH):
            os.mkdir(self.STORE_PATH)
        ALPHA_PATH = os.path.join(self.STORE_PATH, alpha_name)
        if not os.path.exists(ALPHA_PATH):
            os.mkdir(ALPHA_PATH)

        if self.pool is not None:
            alpha = alpha[self.pool == 1] # 资产池内股票的因子值
        alpha = alpha.shift(1)[self.start: self.end] # 回测期间内股票的因子值
        name = f'{alpha_name}_{self.start}_{self.end}_{self.pool_name}'    
        # 计算alpha的指标
        if not os.path.exists(os.path.join(ALPHA_PATH, f'{name}_metrics.csv')):
            self.backtest.backtest(alpha, alpha_name, output = ['metrics'])

        # 读取回测指标
        metrics = pd.read_csv(os.path.join(ALPHA_PATH, f'{name}_metrics.csv'), index_col = 0).T
        metrics['相关系数'] = 1.0
        metrics_list = [metrics]

        # 计算因子相关性
        for pooled_alpha in self.alpha_list.values(): 
            metrics = pooled_alpha['metrics']
            metrics['相关系数'] = corr(alpha, pooled_alpha['alpha'])
            metrics_list.append(metrics)

        # 对比alpha与因子池内因子的指标
        metrics_list = pd.concat(metrics_list, axis = 0)
        if sort_index is not None:
            assert sort_index in metrics_list.columns, f'sort index should be in {metrics_list.columns}'
        display(metrics_list)

        # 绘制相关系数热力图
        plt.figure(figsize = (len(metrics_list), 1))
        ax = sns.heatmap(metrics_list[['相关系数']].rename(columns = {'相关系数': alpha_name}).T, 
                         cmap="YlGnBu", annot=True, linewidths=.5)
        plt.yticks(rotation = 0)
        plt.show()
        
    
