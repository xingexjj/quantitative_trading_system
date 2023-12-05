# quantitative_trading_system
a quantitative trading system on A-shares market  
Python==3.11.5
- [树状结构图](#树状结构图)
- [文件说明](#文件说明)
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
### 文件说明  
使用时, 需要将本repo clone到一个特定的文件夹(`dir/`)下, 要求该文件夹下有`./data`文件夹, 其中包含了回测所需要的`.feather`数据.  
`dir/alpha/`: 用于储存因子结果的文件夹, 回测时自动创建, 在其中为每个因子创建一个文件夹, 储存回测结果.  
`dir/data/`: 储存原始数据的文件夹, 为用户自己的本地数据.  
`dir/dataset/`: 用于储存dataset的文件夹, 首次回测调取数据时自动创建.  
`dir/quantitative_trading_system/requirements.txt`: 系统需要的packages, 可以直接用`pip`安装  
`dir/quantitative_trading_system/test.ipynb`: 用户角度使用系统的样例  
`dir/quantitative_trading_system/mysystem/`: 回测系统  
  ./alphapool.py: 
