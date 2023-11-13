import numpy as np
import pandas as pd
import pickle


PATH = './hs300/'
DUMP_PATH = './alpha/alpha_list/'

class Alpha:
    def __init__(self):
        self.valid = pd.read_pickle(f'{PATH}valid_HS300.pkl')
        self.valid.index = pd.to_datetime(self.valid.index)

        self.close = self.get_data('close')
        self.ret = self.close.pct_change()
        self.open = self.get_data('open')
        self.high = self.get_data('high')
        self.low = self.get_data('low')
        self.vol = self.get_data('vol')
        self.amount = self.get_data('amount')
        self.buy_elg_vol = self.get_data('buy_elg_vol')
        self.sell_elg_vol = self.get_data('sell_elg_vol')
        self.buy_lg_vol = self.get_data('buy_lg_vol')
        self.sell_lg_vol = self.get_data('sell_lg_vol')
        self.buy_md_vol = self.get_data('buy_md_vol')
        self.sell_md_vol = self.get_data('sell_md_vol')
        self.buy_sm_vol = self.get_data('buy_sm_vol')
        self.sell_sm_vol = self.get_data('sell_sm_vol')
        
    def get_data(self, name):
        return pd.read_pickle(f'{PATH}HS300_{name}.pkl')
    
    # def get_alpha(self, alpha, name):
    #     new_alpha = pd.DataFrame(index = alpha.index, columns = alpha.columns)
    #     for i in range(1, len(alpha)):
    #         date1 = alpha.index[i]
    #         date0 = td.get_previous_day(date1.strftime('%Y%m%d'))
    #         new_alpha.loc[date1, self.valid.loc[date0]] = alpha.loc[date1, self.valid.loc[date0]]
    #     new_alpha.index.name = name

    #     with open(f'{DUMP_PATH}{name}.pkl', 'wb') as f:
    #         pickle.dump(new_alpha, f)

    #     return new_alpha
    
    def ret5d(self):
        return self.get_alpha(-self.close.shift(1, fill_value = np.nan) / self.close.shift(6, fill_value = np.nan), 'ret5d')

        