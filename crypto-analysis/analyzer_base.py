import datetime
import logging
import os

import pandas as pd
import statsmodels.api as stats
from pandas.tseries.offsets import BDay

from data_fetcher import get_bitcoin_prices, get_altcoin_prices_from_poloniex

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)


class CryptoAnalyzerBase(object):
    DATA_FOLDER = 'crypto_data'

    BTCUSD = 'btcusd'

    def __init__(self, ticker, hist_start_date=None, refresh=False):
        self.ticker = ticker
        self.refresh = refresh
        self.altcoin_data = pd.DataFrame()
        self.btcusd_data = pd.DataFrame()
        self.hist_start_date = hist_start_date or datetime.datetime.today() - BDay(252)

    @property
    def mean(self):
        raise NotImplementedError("Need to be implemented by sub-classes")

    @property
    def altcoin_returns(self):
        raise NotImplementedError("Need to be implemented by sub-classes")

    @property
    def btcusd_returns(self):
        raise NotImplementedError("Need to be implemented by sub-classes")

    def plot_returns(self):
        raise NotImplementedError("Need to be implemented by sub-classes")

    def plot_returns_against_btcusd(self):
        raise NotImplementedError("Need to be implemented by sub-classes")

    @property
    def beta(self):
        raise NotImplementedError("Need to be implemented by sub-classes")

    @property
    def ols_model(self):
        raise NotImplementedError("Need to be implemented by sub-classes")

    def setup_underlying_data(self, refresh=False):
        if not os.path.exists(self.DATA_FOLDER):
            os.makedirs(self.DATA_FOLDER)

        self.get_btcusd_data(refresh=refresh)
        self.get_altcoin_data(refresh=refresh)

    def get_altcoin_data(self, refresh=False):
        df = pd.DataFrame()
        df = get_altcoin_prices_from_poloniex(self.ticker, self.hist_start_date, datetime.datetime.today(),
                                              refresh=refresh)
        if df.empty:
            logging.error("Unable to get Stock-Data from the Web. Please check connection")
            raise IOError("Unable to get Stock-Data from the Web")
        self.altcoin_data = df

    def get_btcusd_data(self, refresh=False):
        df = pd.DataFrame()
        df = get_bitcoin_prices(refresh=refresh)
        if df.empty:
            logging.error("Unable to get Stock-Data from the Web. Please check connection")
            raise IOError("Unable to get Stock-Data from the Web")

        df.reset_index(inplace=True)
        df.set_index("Date", inplace=True)
        self.btcusd_data = df

    @staticmethod
    def ordinary_least_square_model(asset_returns, index_returns):
        def lin_reg(x, y):
            x = stats.add_constant(x)
            model = stats.OLS(y, x).fit()
            x = x[:, 1]
            return model

        return lin_reg(index_returns.values[-1 * len(asset_returns):], asset_returns.values)
