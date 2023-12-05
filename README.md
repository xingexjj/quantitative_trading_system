# quantitative_trading_system
a quantitative trading system on A-shares market  

- [使用说明](#使用说明)
- [文件说明](#文件说明)
- [树状结构图](#树状结构图)

## 使用说明
系统所使用的Python版本: `Python==3.11.5`  
使用时, 需要将本repo clone到一个特定的文件夹(`dir/`)下, 要求该文件夹下有`./data`文件夹, 其中包含了回测所需要的`.feather`数据.   
在`dir/quantitative_trading_system/test.ipynb`中, 我们给出了用户使用系统的一个样例:  
首先从`dir/quantitative_trading_system/mysystem/`中调取`get_data`函数, `Backtest`类和`Alphapool`类,  
```
from mysystem.dataset import get_data
from mysystem.backtest import Backtest
from mysystem.alphapool import AlphaPool
```
使用`get_data`函数读取数据: `data = get_data(PATH)`, 其中`PATH`设置为本repo (dir/quantitative_trading_system/)的路径, 得到`data`为一个储存各字段数据的字典.  
创建`Backtest`回测类: `backtest = Backtest(PATH, start, end, pool)`, 其中`PATH`设置为本repo (dir/quantitative_trading_system/)的路径,
`start, end`为回测开始和结束的时间, 格式形如‘20221205’, `pool`为选取的资产池, 可选值包括`'all', 'hs300'`, 表示沪深全市场和沪深300成分股.  
根据数据构建因子: 例如计算5日反转因子`ret5d = data['ret'].rolling(5).sum()`.  
使用回测类的回测函数进行回测, 参数包括计算出的因子值和因子名称, 例如对5日反转因子进行回测: `backtest.backtest(ret5d, 'ret5d')`.  
得到的回测结果会储存在`dir/alpha/ret5d`中, 文件名包含了回测区间, 资产池和回测结果类型(包括IC, PnL, 回测指标metrics等).  
下面介绍系统的因子池功能. 创建一个因子池

## 文件说明   
`dir/alpha/`: 用于储存因子结果的文件夹, 回测时自动创建, 在其中为每个因子创建一个文件夹, 储存回测结果.  
`dir/data/`: 储存原始数据的文件夹, 为用户自己的本地数据.  
`dir/dataset/`: 用于储存dataset的文件夹, 首次回测调取数据时自动创建.  
`dir/quantitative_trading_system/requirements.txt`: 系统需要的packages, 可以直接用`pip`安装  
`dir/quantitative_trading_system/test.ipynb`: 用户角度使用系统的样例  
`dir/quantitative_trading_system/mysystem/`: 回测系统  
>`./alphapool.py`: 因子池  
>`./backtest.py`: 回测  
>`./dataset.py`: 将原始数据处理为dataset  
>`./utils.py`: 构建因子可能用到的工具

`dir/quantitative_trading_system/newdata`: 添加的新数据  
>`./get_hs300_data.ipynb`: 获取沪深300成分股数据  
>`./get_suspend_data.ipynb`: 获取停牌数据  
>`./hs300.csv`: 沪深300成分股数据  
>`./suspend.csv`: 停牌数据

## 树状结构图
```
dir/  
│  
├─alpha  
│  ├─alpha1  
│  │      alpha1_20200101_20221231_all_metrics.csv  
│  │      ...  
│  │      
│  ├─alpha2  
│  │      ...  
│  │  
│  └─...  
│           
├─data  
│      stk_daily.feather  
│      ...  
│       
├─dataset  
│      data.pkl  
│       
└─quantitative_trading_system (this repo)  
    │  .gitignore  
    │  LICENSE  
    │  README.md  
    │  requirements.txt  
    │  test.ipynb  
    │   
    ├─mysystem  
    │     alphapool.py  
    │     backtest.py  
    │     dataset.py  
    │     utils.py  
    │          
    └─newdata  
            get_hs300_data.ipynb  
            get_suspend_data.ipynb  
            hs300.csv  
            suspend.csv
```
