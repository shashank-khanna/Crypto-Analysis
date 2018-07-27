import logging

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import style
from mpl_finance import candlestick_ohlc

from analyzer_base import CryptoAnalyzerBase

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)

style.use('ggplot')


class BitcoinAnalyzer(CryptoAnalyzerBase):

    def __init__(self, refresh=False):
        super(BitcoinAnalyzer, self).__init__('BTCUSD', refresh=refresh)
        self.get_btcusd_data(refresh=refresh)

    @property
    def mean(self):
        return self.btcusd_data['Mean'].mean()

    @property
    def std(self):
        return self.btcusd_data['Mean'].std()

    @property
    def altcoin_returns(self):
        pass

    @property
    def btcusd_returns(self):
        if self.btcusd_data.empty:
            raise ValueError("Historical BTC prices unavailable")
        self.btcusd_data['returns'] = self.btcusd_data['Mean'].pct_change()
        return self.btcusd_data.returns[1:]

    def plot_returns(self):
        # self.btcusd_data.ix[:, self.btcusd_data.columns.difference(['Volume'])].plot()
        self.btcusd_data['returns'].plot()
        plt.ylabel("Daily Returns of Bitcoin ")
        plt.show()

    def plot_candlestick(self):
        df_ohlc = self.btcusd_data['Mean'].resample('4D').ohlc()
        df_volume = self.btcusd_data['Volume'].resample('4D').sum()
        df_ohlc = df_ohlc.reset_index()
        df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)

        fig = plt.figure(figsize=(20, 10))
        plt.xlabel('Date')
        plt.ylabel('Price')

        plt.title(self.ticker)
        plt.legend()
        plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0.8)

        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
        ax1.xaxis_date()

        candlestick_ohlc(ax1, df_ohlc.values, width=3, colorup='#77d879', colordown='#db3f3f')
        # ax2.bar(df_volume.index.map(mdates.date2num), df_volume.values)
        ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)
        plt.show()

    def plot_moving_averages(self, window1=14, window2=42):
        self.btcusd_data['%dDay' % window1] = self.btcusd_data['Mean'].rolling(window=window1).mean()
        self.btcusd_data['%dDay' % window2] = self.btcusd_data['Mean'].rolling(window=window2).mean()
        self.btcusd_data[['Mean', '%dDay' % window1, '%dDay' % window2]].plot()
        plt.show()

    def plot_returns_against_btcusd(self):
        pass

    @property
    def beta(self):
        pass

    @property
    def ols_model(self):
        pass


if __name__ == '__main__':
    analyzer = BitcoinAnalyzer()
    print(analyzer.btcusd_returns.head())
    analyzer.plot_returns()
    # analyzer.plot_candlestick()
    analyzer.plot_moving_averages(50, 200)
    print("Mean ", analyzer.mean)
    print("STD ", analyzer.std)
