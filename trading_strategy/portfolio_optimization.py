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
sharpe_ratio = []

for _ in range(30000):
    weights = np.random.random(len(stocks))
    weights /= np.sum(weights)

    returns = np.dot(weights, annual_ret)
    risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

    port_ret.append(returns)
    port_risk.append(risk)
    port_weights.append(weights)
    sharpe_ratio.append(returns/risk)

portfolio = {'Returns':port_ret, 'Risk':port_risk, 'Sharpe':sharpe_ratio}
for i,s in enumerate(stocks):
    portfolio[s] = [weight[i] for weight in port_weights]
df = pd.DataFrame(portfolio)
df = df[['Returns','Risk','Sharpe'] + [s for s in stocks]]
#print(df)

max_sharpe = df.loc[df['Sharpe'] == df['Sharpe'].max()]
min_risk = df.loc[df['Risk'] == df['Risk'].min()]

print('max_shapre >>')
newdf = df.sort_values(by=['Sharpe'],ascending=False)
print(newdf)
print('min_risk >>')
newdf = df.sort_values(by=['Risk'],ascending=True)
print(newdf)

df.plot.scatter(x='Risk', y='Returns', c='Sharpe', cmap='viridis', edgecolors='k', figsize=(11,7), grid=True)
plt.scatter(x=max_sharpe['Risk'], y=max_sharpe['Returns'], c='r', marker='*', s=300)
plt.scatter(x=min_risk['Risk'], y=min_risk['Returns'], c='r', marker='X', s=200)
plt.title('Portfilio Optimization')
plt.xlabel('Risk')
plt.ylabel('Expected Returns')
plt.show()
