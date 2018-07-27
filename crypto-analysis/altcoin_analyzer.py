import logging

import matplotlib.pyplot as plt
from matplotlib import style

from analyzer_base import CryptoAnalyzerBase

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)

style.use('ggplot')


class AltcoinAnalyzer(CryptoAnalyzerBase):

    def __init__(self, altcoin, refresh=False):
        super(AltcoinAnalyzer, self).__init__(altcoin, refresh=refresh)
        self.get_altcoin_data(refresh=refresh)
        self.get_btcusd_data(refresh=refresh)
        self.get_altcoin_prices_in_usd()

    def get_altcoin_prices_in_usd(self):
        self.altcoin_data['altPriceUSD'] = self.altcoin_data['weightedAverage'] * \
                                           self.btcusd_data['Mean'].values[
                                           -1 * len(self.altcoin_data['weightedAverage']):]

    @property
    def mean(self):
        return self.altcoin_data['weightedAverage'].mean()

    @property
    def std(self):
        return self.altcoin_data['weightedAverage'].std()

    @property
    def altcoin_returns(self):
        if self.altcoin_data.empty:
            raise ValueError("Historical %s prices unavailable" % self.ticker)
        self.altcoin_data['returns'] = self.altcoin_data['weightedAverage'].pct_change()
        return self.altcoin_data['returns']  # [1:]

    @property
    def altcoin_usd_returns(self):
        if self.altcoin_data.empty:
            raise ValueError("Historical %s prices unavailable" % self.ticker)
        self.altcoin_data['returnsUSD'] = self.altcoin_data['altPriceUSD'].pct_change()
        return self.altcoin_data['returnsUSD']  # [1:]

    @property
    def btcusd_returns(self):
        if self.btcusd_data.empty:
            raise ValueError("Historical BTC prices unavailable")
        self.btcusd_data['returns'] = self.btcusd_data['Mean'].pct_change()
        return self.btcusd_data.returns[1:]

    def plot_returns(self):
        self.btcusd_data['returns'].plot()
        plt.ylabel("Daily Returns of Bitcoin ")
        plt.show()

    def plot_usd_returns_against_btcusd(self):
        plt.figure(figsize=(10, 5))
        self.altcoin_usd_returns.plot()
        self.btcusd_data.plot()
        plt.ylabel("Daily Returns of %s against Bitcoin" % self.ticker)
        plt.show()

    @property
    def alpha(self):
        return self.ols_model.params[0]

    @property
    def beta(self):
        return self.ols_model.params[1]

    @property
    def ols_model(self):
        return CryptoAnalyzerBase.ordinary_least_square_model(self.altcoin_data['altPriceUSD'],
                                                              self.btcusd_data['Mean'])

    def plot_moving_averages(self, window1=14, window2=42):
        self.altcoin_data['%dDay' % window1] = self.altcoin_data['altPriceUSD'].rolling(window=window1).mean()
        self.altcoin_data['%dDay' % window2] = self.altcoin_data['altPriceUSD'].rolling(window=window2).mean()
        self.altcoin_data[['altPriceUSD', '%dDay' % window1, '%dDay' % window2]].plot()
        plt.show()


if __name__ == '__main__':
    analyzer = AltcoinAnalyzer('ETH', refresh=True)
    print(analyzer.btcusd_returns.head())
    print(analyzer.altcoin_returns.head())
    print(analyzer.altcoin_usd_returns.head())
    analyzer.plot_returns()
    # analyzer.plot_candlestick()
    analyzer.plot_moving_averages(50, 200)
    print("Mean ", analyzer.mean)
    print("STD ", analyzer.std)
    print("Alpha ", analyzer.alpha)
    print("Beta ", analyzer.beta)
