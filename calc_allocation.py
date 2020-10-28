from load_data import securities_pct, securities_df
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import norgatedata
from datetime import datetime

ma_period = 50

# creating a DataFrame consisting of the moving averages for each stock in securities_df
securities_ma = securities_df.rolling(ma_period).mean()
securities_ma.dropna(axis=0, inplace=True)
# adjust the length of the original DataFrames to start once the moving average period is calculated
securities_df, securities_pct = securities_df.loc[securities_ma.index[0]:], securities_pct.loc[securities_ma.index[0]:]

# DataFrame which says whether we have a position in a given security
# based on that security's price relative to it's moving average
positions = pd.DataFrame(data=None, columns=securities_df.columns, index=securities_df.index)

for security in securities_df.columns:

    # setting the value of long positions to 1. When the stock price > ma
    positions.loc[securities_df[security].shift(1) > securities_ma[security], security] = 1

# setting the value of short/no position to 0
positions.fillna(0, inplace=True)

# creating the DataFrame that will store the cumulative returns for each ticker's sma strategy
returns = pd.DataFrame(data=None, columns=securities_df.columns, index=securities_df.index)

for security in positions.columns:

    # the return column for each respective security is equal to 1 + the cumulative product of the position value
    # multiplied by the daily pct return of that security
    returns[security] = np.cumprod(1 + (positions[security] * securities_pct[security]))

returns.plot()
plt.show()

