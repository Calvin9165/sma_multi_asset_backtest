from load_data import securities_pct, securities_df
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import norgatedata
from datetime import datetime

ma_period = 50

# creating a DataFrame consisting of the moving averages for each stock in securities_df
securities_ma = securities_df.rolling(ma_period).mean()

# adjust the length of the original DataFrames to start once the moving average period is calculated
securities_df, securities_pct = securities_df.loc[securities_ma.index[0]:], securities_pct.loc[securities_ma.index[0]:]

fig = plt.figure()

ax1 = fig.add_subplot()
ax1.plot(securities_df)
ax1.plot(securities_ma)

plt.show()