from load_data import securities_pct, securities_df
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import norgatedata
from datetime import datetime

from perf_funcs import *

ma_period = 50

# creating a DataFrame consisting of the moving averages for each stock in securities_df
securities_ma = securities_df.rolling(ma_period).mean()
securities_ma.dropna(axis=0, inplace=True)
# adjust the length of the original DataFrames to start once the moving average period is calculated
securities_df, securities_pct = securities_df.loc[securities_ma.index[0]:], securities_pct.loc[securities_ma.index[0]:]

# DataFrame which says whether we have a position in a given security
# based on that security's price relative to it's moving average
positions_pct = pd.DataFrame(data=None, columns=securities_df.columns, index=securities_df.index)

for security in securities_df.columns:

    # setting the value of long positions to 1. When the stock price > ma
    positions_pct.loc[securities_df[security].shift(1) > securities_ma[security], security] = 1

# setting the value of short/no position to 0
positions_pct.fillna(0, inplace=True)

# creating the DataFrame that will store the cumulative returns for each ticker's sma strategy
returns = pd.DataFrame(data=None, columns=securities_df.columns, index=securities_df.index)

for security in positions_pct.columns:

    # the return column for each respective security is on a daily basis, position multiplied by daily return
    returns[security] = (positions_pct[security] * securities_pct[security])

# the initial $ value being invested in the portfolio
invested = 1000

# the frequency with which we'll rebalance the portfolio
rebal_freq = 21

# creating the DataFrame that will store the $ value of the total portfolio and setting initial value to invested
portfolio_value = pd.DataFrame(data=None, columns=['Portfolio'], index=returns.index)
portfolio_value.iloc[0]['Portfolio'] = invested

# pnl_stocks will hold the net PnL Data for each stock over the entire backtest
pnl_positions = pd.DataFrame(data=0, columns=returns.columns, index=returns.index)

# the $ value allocated in each position
positions = pd.DataFrame(data=None, columns=returns.columns, index=returns.index)

# the common date index between returns, securities_pct
dates = securities_pct.index

# main loop of the backtest
for t in range(0, len(dates), rebal_freq):

    num_stocks = len(securities_pct.columns)

    if t == 0:
        rb_day = dates[t]
    else:
        rb_day = dates[t + 1]

    # the day that we rebalance the portfolio, use this value in portfolio_value to calculate allocation
    rb_value = dates[t]

    try:
        rb_end = dates[t + rebal_freq]
    except IndexError:
        rb_end = dates[-1]

    for position in positions:
        positions.loc[rb_day: rb_end, position] = (portfolio_value['Portfolio'][rb_value] / num_stocks) * np.cumprod(1 + returns.loc[rb_day: rb_end, position])
        pnl_positions.loc[rb_day:rb_end, position] = (positions.loc[rb_day:rb_end, position] - portfolio_value['Portfolio'][rb_value] / num_stocks) + pnl_positions.loc[rb_value, position]

    portfolio_value.loc[rb_day: rb_end, 'Portfolio'] = np.nansum(positions.loc[rb_day: rb_end], axis=1)

if __name__ == '__main__':

    # creating the index to compare our strategy to
    index = create_index(start=portfolio_value.index[0],
                         end=portfolio_value.index[-1],
                         index_ticker='SPY')

    # same initial investment as our backtested strategy
    index = index * invested

    # CAGR
    strat_cagr = cagr(portfolio_value['Portfolio'])
    strat_cagr = '{:.2%}'.format(strat_cagr)

    # drawdowns
    drawdowns = drawdowns(portfolio_value['Portfolio'])
    max_dd = min(drawdowns.fillna(0))
    max_dd = '{:.2%}'.format(max_dd)

    # volatility
    vol = volatility(portfolio_value['Portfolio'])
    vol = '{:.2%}'.format(vol)

    strat_start = portfolio_value.index[0].strftime('%Y-%m-%d')
    strat_end = portfolio_value.index[-1].strftime('%Y-%m-%d')

    # plotting the performance of our backtest with an index
    perf_chart = backtest_perf_plot(equity_curve=portfolio_value,
                                    rolling_dd=drawdowns,
                                    position_pnl=pnl_positions,
                                    comparison=True,
                                    index=index)
    plt.show()

    print('The CAGR for Risk Parity from {} to {} was {} with an annualized volatility of {}'.format(strat_start,
                                                                                                     strat_end,
                                                                                                     strat_cagr,
                                                                                                     vol))

    print('The Max Drawdown for Risk Parity between {} and {} was {}'.format(strat_start,
                                                                             strat_end,
                                                                             max_dd))