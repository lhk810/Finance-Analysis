#pip install : numpy, pandas,  matplotlib, yfinance, pandas_datareader, scipy

import sys
import pandas_datareader as pdr
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from scipy import stats

def get_stock(name, start=datetime.datetime(2020,1,1), end=datetime.datetime(2020,12,30)):
    return pdr.DataReader(name, 'yahoo', start, end)

def show_close(name, linedef='r'):
    stockdata = get_stock(name)
    plt.plot(stockdata.index, stockdata.Close, linedef, label=name)
    #plt.plot(msft.index, msft.Close, 'r--', label='Microsoft')
    plt.legend(loc='best')
    plt.show()

def make_daily_change(name):
    stockdata=get_stock(name)
    res = (stockdata['Close']/stockdata['Close'].shift(1)-1)*100
    res.iloc[0] = 0 #before this line, it was NaN
    return res

def show_daily_earn(name):
    daily_change=make_daily_change(name)
    earn = daily_change.cumsum()
    plt.plot(earn.index, earn, 'b', label=name)
    plt.ylabel('Change %')
    plt.grid(True)
    plt.legend(loc='best')
    plt.show()

def make_mdd(name, window=252):
    stockdata = get_stock(name)
    peak = stockdata['Adj Close'].rolling(window,min_periods=1).max()
    drawdown = stockdata['Adj Close']/peak - 1.0
    max_dd = drawdown.rolling(window, min_periods=1).min()
    return max_dd, drawdown, stockdata

def show_mdd(name):
    max_dd, drawdown, stockdata = make_mdd(name)
    fig = plt.figure()
    subplot1 = fig.add_subplot(2,1,1)
    subplot1.plot(stockdata.index, stockdata['Adj Close'].values, 'r', label=name)
    subplot1.grid(True)
    subplot1.legend(loc='best')
    subplot2 = fig.add_subplot(2,1,2)
    subplot2.plot(drawdown.index, drawdown.values, 'b', label=name+' DD')
    subplot2.plot(max_dd.index, max_dd.values, 'r', label=name+' MDD')
    subplot2.grid(True)
    subplot2.legend(loc='best')
    plt.show()

def compare_index(name1='^DJI',name2='^KS11'):
    stock1 = get_stock(name1)
    stock2 = get_stock(name2)
    stock1 = stock1['Close']/stock1['Close'].iloc[0]*100
    stock2 = stock2['Close']/stock2['Close'].iloc[0]*100
    plt.figure()
    plt.plot(stock1.index, stock1, 'r--', label='Dow Jones Industrial Average' if name1=='^DJI' else name1)
    plt.plot(stock1.index, stock2, 'b', label='KOSPI' if name2=='^KS11' else name2)
    plt.grid(True)
    plt.legend(loc='best')
    plt.show()

def compare_index_scatter(name1='^DJI',name2='^KS11'):
    stock1 = get_stock(name1)
    stock2 = get_stock(name2)
    df = pd.DataFrame({name1:stock1['Close'], name2:stock2['Close']})
    df = df.fillna(method='bfill') #remove NaN
    df = df.fillna(method='ffill')
    plt.figure()
    plt.scatter(df[name1], df[name2], marker='.')
    plt.xlabel('Dow Jones Industrial Average' if name1=='^DJI' else name1)
    plt.ylabel('KOSPI' if name2=='^KS11' else name2)
    plt.show()

def find_correlation(name1='^DJI',name2='^KS11'):
    stock1 = get_stock(name1)
    stock2 = get_stock(name2)
    df = pd.DataFrame({name1:stock1['Close'], name2:stock2['Close']})
    df = df.fillna(method='bfill') #remove NaN
    df = df.fillna(method='ffill')
    regr = stats.linregress(df[name1], df[name2])
    regr_line = f'Y = {regr.slope:.2f} * X + {regr.intercept:.2f}'
    plt.figure()
    plt.plot(df[name1], df[name2], '.')
    plt.plot(df[name1], regr.slope * df[name1] + regr.intercept, 'r')
    plt.legend([f'{name1} x {name2}', regr_line])
    plt.title(f'{name1} x {name2} (R = {regr.rvalue:.2f})')
    plt.xlabel('Dow Jones Industrial Average' if name1=='^DJI' else name1)
    plt.ylabel('KOSPI' if name2=='^KS11' else name2)
    plt.show()

#stockname = 'ESTC'

#show_close(get_stock('AMD'),'r','AMD')
#show_daily_earn(make_daily_change(get_stock(stockname)), stockname)

stockname='ESTC'
if len(sys.argv)==1:
    show_daily_earn(stockname)
elif len(sys.argv)==2:
    stockname = sys.argv[1]
    if stockname == 'compare_index':
        compare_index()
    elif stockname == 'compare_index_scatter':
        compare_index_scatter()
    elif stockname == 'find_correlation':
        find_correlation()
    else:
        show_daily_earn(stockname)
elif len(sys.argv)==3:
    stockname = sys.argv[1]
    if sys.argv[2]=='show_close':
        show_close(stockname)
    elif sys.argv[2]=='showEarn':
        show_daily_earn(stockname)
    elif sys.argv[2]=='showMDD':
        show_mdd(stockname)
    else:
        print('그런 기능 없음 ㅎ')
elif len(sys.argv)==4:
    method = sys.argv[1]
    if method == 'compare_index':
        compare_index(sys.argv[2], sys.argv[3])
    elif method == 'compare_index_scatter':
        compare_index_scatter(sys.argv[2], sys.argv[3])
    elif method == 'find_correlation':
        find_correlation(sys.argv[2], sys.argv[3])
    else:
        print('그런 기능 없음 ㅎㅎ')
else:
    print('인자수가 안 맞음 ㅎ')
