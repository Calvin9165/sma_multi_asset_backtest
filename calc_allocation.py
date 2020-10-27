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

fig = plt.figure()

# ax1 = fig.add_subplot()
# ax1.plot(securities_df)
# ax1.plot(securities_ma)
#
# plt.show()

# DataFrame which says whether we have a position in a given security based on that security's price relative to it's moving average
positions = pd.DataFrame(data=None, columns=securities_df.columns, index=securities_df.index)

for security in securities_df:

    # setting the value of long positions to 1. When the stock price > ma
    positions.loc[securities_df[security].shift(1) > securities_ma[security], security] = 1

# setting the value of short/no position to 0
positions.fillna(0, inplace=True)

positions['XLE'].plot()
plt.show()

