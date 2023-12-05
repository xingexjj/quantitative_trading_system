import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display # 展示pd.DataFrame的函数

import os
from typing import Optional
from .dataset import get_data

# 设置plt负号和中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class Backtest:
    '''
    回测类 \n
    PATH: 存储数据的路径, 设置为本repo的路径 \n
    start: 回测开始的时间, 例如'20200101' \n
    end: 回测结束的时间, 例如'20221231' \n
    init_cap: 总资金 \n
    pool: 资产池, 目前支持的可选项有'all'(沪深全市场), 'hs300'(沪深300成分股, 实时跟踪),
    也可直接传入一个one-hot的pd.DataFrame \n
    output: 回测输出, 可选项包括ic, pnl, weight, metrics
    '''
    def __init__(self, PATH: str, start: str, end: str, init_cap: float = 1e8, 
                 pool = 'all', output: list = ['ic', 'pnl', 'metrics']) -> None:
        self.PATH = PATH
        self.STORE_PATH = os.path.join(PATH, '../alpha/') # 储存回测结果的路径
        self.ret = get_data(PATH)['ret'].shift(-1) # 收益率
        self.start = start
        self.end = end
        self.init_cap = init_cap
        self.pool_name, self.pool = self.get_pool(pool)
        self.output = output

    def get_pool(self, pool) -> (str, Optional[pd.DataFrame]):
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

    def get_ic(self, alpha: pd.DataFrame) -> pd.DataFrame:
        '''
        计算IC, rankIC
        '''
        ic = pd.DataFrame(index = alpha.index, columns = ['IC', 'rankIC'])
        for date in alpha.index:
            ic.loc[date, 'IC'] = alpha.loc[date].corr(self.ret.loc[date])
            ic.loc[date, 'rankIC'] = alpha.loc[date].corr(self.ret.loc[date], method = 'spearman')
        return ic        

    def plot_ic(self, ic: pd.Series, ALPHA_PATH: str, name: str) -> None:
        '''
        绘制累积IC曲线
        '''
        ic_mean = ic.mean(axis = 0).astype('float').round(4) # IC均值, 设置小数位数
        icir = (ic.mean(axis = 0) / ic.std(axis = 0)).astype('float').round(4) # ICIR, 设置小数位数
        plt.figure(figsize = (8, 4))
        plt.plot(ic.cumsum()) # IC累积值
        plt.title(f'{name}_IC')
        plt.legend([f'IC mean = {ic_mean["IC"]} \nICIR = {icir["IC"]}', \
                    f'rankIC mean = {ic_mean["rankIC"]} \nrankICIR = {icir["rankIC"]}'])
        plt.xlabel('date')
        plt.ylabel('ic_cumsum', rotation = 0, labelpad = 10)
        plt.grid()
        plt.savefig(os.path.join(ALPHA_PATH, f'{name}_IC.jpg'))

    def get_weight(self, alpha: pd.DataFrame) -> pd.DataFrame:
        '''
        计算权重
        '''
        abssum = abs(alpha).sum(axis = 1) # 计算权重绝对值的截面和
        weight = (alpha.T / abssum[abssum > 1e-8]).T.fillna(0) # 归一化, 每个截面上, 权重绝对值之和为1
        return weight
    
    def get_pnl(self, weight: pd.DataFrame, init_cap) -> pd.Series:
        '''
        计算PnL
        '''
        portfolio_ret = (weight * self.ret).sum(axis = 1).shift(1).fillna(0) # 计算组合每日的收益率
        pnl = init_cap * (1 + portfolio_ret.cumsum())
        return pnl
    
    def plot_pnl(self, pnl: pd.Series, ALPHA_PATH: str, name: str) -> None:
        '''
        绘制PnL曲线
        '''
        ret = pnl.pct_change()
        ret_mean = (ret.mean() * 252).round(4)
        sharpe_ratio = ((ret.mean() / ret.std()) * np.sqrt(252)).round(4)
        plt.figure(figsize = (8, 4))
        plt.plot(pnl)
        plt.title(f'{name}_PnL')
        plt.legend([f'annually ret = {ret_mean} \nSharpe ratio = {sharpe_ratio}'])
        plt.xlabel('date')
        plt.ylabel('PnL', rotation = 0, labelpad = 10)
        plt.grid()
        plt.savefig(os.path.join(ALPHA_PATH, f'{name}_PnL.jpg'))

    def max_drawdown(self, pnl: pd.Series) -> float:
        '''
        计算最大回撤
        '''
        pnl = pnl.values
        max_drawdown = 0 # 记录最大回撤
        max_value = pnl[0] # 记录目前PnL的最大值
        for v in pnl[1:]:
            if v > max_value:
                max_value = v
            else:
                max_drawdown = max(max_drawdown, max_value - v)
        return max_drawdown / pnl[0]

    def get_metrics(self, ic: pd.Series, pnl: pd.Series, ALPHA_PATH: str, name: str) -> None:
        '''
        计算指标
        '''
        ic_mean = ic.mean(axis = 0).astype('float').round(4) # IC均值
        icir = (ic.mean(axis = 0) / ic.std(axis = 0)).astype('float').round(4) # ICIR
        ret = pnl.pct_change()
        ret_mean = (ret.mean() * 252).round(4) # 年化收益率
        ret_std = (ret.std() * np.sqrt(252)).round(4) # 年化波动率
        sharpe_ratio = ((ret.mean() / ret.std()) * np.sqrt(252)).round(4) # 夏普比率
        max_drawdown = self.max_drawdown(pnl) # 最大回撤
        winning_rate = (ret > 0).mean().round(4) # 胜率
        metrics = pd.DataFrame([ic_mean['IC'], icir['IC'], ic_mean['rankIC'], icir['rankIC'], 
                                ret_mean, ret_std, sharpe_ratio, max_drawdown, winning_rate],
                                index = ['IC均值', 'ICIR', 'rankIC均值', 'rankICIR',
                                         '年化收益率', '年化波动率', '夏普比率', 
                                         '最大回撤', '胜率'],
                                columns = [name.split('_')[0]])
        metrics.to_csv(os.path.join(ALPHA_PATH, f'{name}_metrics.csv'))
        display(metrics) # 展示指标DataFrame


    def backtest(self, alpha: pd.DataFrame, alpha_name: str,
                 start: Optional[str] = None, end: Optional[str] = None, 
                 init_cap: Optional[float] = None, pool = None, 
                 output: Optional[list] = None) -> None:
        '''
        回测函数: \n
        alpha: 需要回测的因子
        alpha_name: 因子名称
        下面参数与回测类参数相同, 如不传入, 默认为回测类参数值
        start: 回测开始的时间, 例如'20200101' \n
        end: 回测结束的时间, 例如'20221231' \n
        init_cap: 总资金 \n
        pool: 资产池, 目前支持的可选项有'all'(沪深全市场), 'hs300'(沪深300成分股, 实时跟踪),
        也可直接传入一个one-hot的pd.DataFrame \n
        output: 回测输出, 可选项包括ic, pnl, weight, metrics
        '''
        # 检查, 创建储存回测结果的路径
        if not os.path.exists(self.STORE_PATH):
            os.mkdir(self.STORE_PATH)
        ALPHA_PATH = os.path.join(self.STORE_PATH, alpha_name)
        if not os.path.exists(ALPHA_PATH):
            os.mkdir(ALPHA_PATH)

        # 将未传入的参数设为与回测类一致
        if start is None:
            start = self.start
        if end is None:
            end = self.end
        if init_cap is None:
            init_cap = self.init_cap
        if pool is None:
            pool_name, pool = self.pool_name, self.pool
        else:
            pool_name, pool = self.get_pool(pool)
        if output is None:
            output = self.output

        if pool is not None:
            alpha = alpha[pool == 1] # 资产池内股票的因子值
        alpha = alpha.shift(1).loc[start: end] # 回测期间内股票的因子值
        name = f'{alpha_name}_{start}_{end}_{pool_name}'

        print(f'Start backtesting alpha {alpha_name}')

        # 计算IC, rankIC
        ic = self.get_ic(alpha)
        
        if 'ic' in output:
            ic.to_csv(os.path.join(ALPHA_PATH, f'{name}_IC.csv'))
            self.plot_ic(ic, ALPHA_PATH, name) # 绘制累积IC曲线
        
        if ic['IC'].mean() < 0:
            alpha = -alpha    

        # 计算权重
        weight = self.get_weight(alpha)
        if 'weight' in output:
            weight.to_csv(os.path.join(ALPHA_PATH, f'{name}_weight.csv'))
            
        # 计算PnL
        pnl = self.get_pnl(weight, init_cap)
        pnl = pnl[start: end]
        if 'pnl' in output:
            pnl.to_csv(os.path.join(ALPHA_PATH, f'{name}_PnL.csv'))
            self.plot_pnl(pnl, ALPHA_PATH, name) # 绘制累积IC曲线

        # 计算回测指标
        if 'metrics' in output:
            self.get_metrics(ic, pnl, ALPHA_PATH, name)

        print(f'Successfully backtest alpha {alpha_name} and store results to {ALPHA_PATH}')