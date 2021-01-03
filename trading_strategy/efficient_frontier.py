import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import Analyzer

args = []
for line in sys.stdin.read().split('\n'):
    if line!='':
        args.append(line)

if len(args)==1:
    print("need a argument for choose KR | global")
    sys.exit()
if len(args)>1:
    mk = Analyzer.MarketDB(args[0])

stocks = []
for i in range(1, len(args)):
    stocks.append(args[i])

df = pd.DataFrame()
for s in stocks:
    df[s] = mk.get_daily_price(s, '2016-01-01', '2020-12-31')['close']

daily_ret = df.pct_change()
annual_ret = daily_ret.mean() * 252
daily_cov = daily_ret.cov()
annual_cov = daily_cov * 252

port_ret = []
port_risk = []
port_weights = []
for _ in range(30000):
    weights = np.random.random(len(stocks))
    weights /= np.sum(weights)

    returns = np.dot(weights, annual_ret)
    risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

    port_ret.append(returns)
    port_risk.append(risk)
    port_weights.append(weights)

portfolio = {'Returns':port_ret, 'Risk':port_risk}
for i,s in enumerate(stocks):
    portfolio[s] = [weights[i] for weight in port_weights]
df = pd.DataFrame(portfolio)
df = df[['Returns','Risk'] + [s for s in stocks]]

df.plot.scatter(x='Risk', y='Returns', figsize=(8,6), grid=True)
plt.title('Efficient Frontier')
plt.xlabel('Risk')
plt.ylabel('Expected Returns')
plt.show()
