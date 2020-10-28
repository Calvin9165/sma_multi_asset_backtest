from datetime import datetime, timedelta
import pandas as pd
from math import sqrt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import norgatedata
import numpy as np

def drawdowns(strategy_series):
    """
    :param strategy_series: float, price or dollar value of strategy/asset/stock we want to measure drawdowns for
    :return: float, daily drawdown values
    """

    return strategy_series / strategy_series.cummax() - 1


def cagr(strategy_series, data_freq='calendar'):
    """
    :param strategy_series: float, price or dollar value of strategy/asset/stock we want to measure CAGR for
    :param data_freq: string, the frequency with which the data is produced. This is only taken into account
        if the index of strategy_series are integers
    :return: float, the CAGR over the entire time period for the strategy/asset/stock in question
    """

    # TODO Question to think about: Should we even let the cagr function work if the index provided is not a datetime
    #   index?

    # the number of days used on our denominator 365 for all cases, except data without datetime index
    num_days = timedelta(days=365)

    # beginning and ending value for the strategy/asset/stock in question
    start_val = strategy_series.iloc[0]
    end_val = strategy_series.iloc[-1]

    # the starting and ending date for the strategy/asset/stock in question
    start_date = strategy_series.index[0]
    end_date = strategy_series.index[-1]

    # if index of series is a datetime index
    if type(strategy_series.index) is pd.DatetimeIndex:

        # period is equal to number of years the strategy has been invested for as a float
        period = (end_date - start_date) / num_days

        return ((end_val / start_val) ** (1 / period)) - 1

    # if index is not a datetime index
    else:

        # if the trading data includes all calendar days
        if data_freq == 'calendar':

            period = (end_date - start_date) / num_days

            return ((end_val / start_val) ** (1 / period)) - 1

        # if the trading data only includes trading days
        elif data_freq == 'trade':

            num_days = 252

            period = (end_date - start_date) / num_days

            return ((end_val / start_val) ** (1 / period)) - 1


def volatility(strategy_series):

    """
    :param strategy_series: float time series, price or dollar value of strategy/asset/stock we want to
        measure volatility for
    :return: float time series, the volatility over the entire period for the strategy/asset/stock in question
    """

    # the daily percent change for the strategy_series
    daily_change = strategy_series.pct_change()

    vol = daily_change.std() * sqrt(252)

    return vol


def backtest_perf_plot(equity_curve, rolling_dd, position_pnl, comparison=False, index=None):
    fig = plt.figure(figsize=(10, 7))

    ax1 = fig.add_subplot(3, 1, 1)
    ax1.plot(equity_curve, label='Backtest')

    formatter = ticker.StrMethodFormatter('${x:,.0f}')
    ax1.yaxis.set_major_formatter(formatter)

    # plotting the backtest drawdowns
    ax2 = fig.add_subplot(3, 1, 2)
    ax2.plot(rolling_dd, label='Backtest')

    # Just keep it simple here - we're going to be using csv data for the course so don't need to load in fresh data
    if comparison is True:

        # plotting the index value
        ax1.plot(index, label='Index')
        # plotting the index drawdowns
        ax2.plot(drawdowns(index), label='Index')

    pct_formatter = ticker.PercentFormatter(1, decimals=0)
    ax2.yaxis.set_major_formatter(pct_formatter)

    # plotting the PnL for individual positions
    ax3 = fig.add_subplot(3, 1, 3)

    for position in position_pnl:
        ax3.plot(position_pnl[position], label=position)

    formatter = ticker.StrMethodFormatter('${x:,.0f}')
    ax3.yaxis.set_major_formatter(formatter)

    ax1.legend()
    ax2.legend()
    # ax3.legend()

    return fig

def create_index(start, end, index_ticker):
    symbol = index_ticker

    norgate_df = norgatedata.price_timeseries(symbol,
                                              start_date=start,
                                              end_date=end,
                                              interval='D',
                                              format='pandas-dataframe')

    norgate_df.drop(['Open', 'High', 'Low', 'Volume', 'Turnover',
                     'Unadjusted Close', 'Dividend'], axis=1, inplace=True)

    # changing name from Close to whatever the ticker is
    norgate_df.rename({'Close': index_ticker}, inplace=True, axis=1)

    # return the cumulative pct return over the period we have the data for
    norgate_df[index_ticker] = np.cumprod(1 + norgate_df[index_ticker].pct_change())

    return norgate_df