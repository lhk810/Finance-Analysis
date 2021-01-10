import pandas as pd
from datetime import datetime
from datetime import timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import Analyzer

class MakeMessage:
    def __init__(self):
        self.target_date = (datetime.today()-timedelta(days=7)).date()
    
    def by_band_reversal(self):
        KR_buy = {}
        KR_sell = {}
        global_buy = {}
        global_sell = {}

        mk = Analyzer.MarketDB('KR')
        for i,code in enumerate(mk.codes):

            buy_date = []
            sell_date = []
            df = mk.get_daily_price(code, '2019-01-01')

            df['MA20'] = df['close'].rolling(window=20).mean()
            df['stddev'] = df['close'].rolling(window=20).std()
            df['upper'] = df['MA20'] + (df['stddev'] * 2)
            df['lower'] = df['MA20'] - (df['stddev'] * 2)
            df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])

            df['II'] = (2*df['close']-df['high']-df['low'])/(df['high']-df['low'])*df['volume']
            df['IIP21'] = df['II'].rolling(window=21).sum()/df['volume'].rolling(window=21).sum()*100
            df = df.dropna()

            for i in range(0, len(df.close)):
                if df.index.values[i] > self.target_date and df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:
                    buy_date.append(df.index.values[i].strftime('%Y-%m-%d'))
                elif df.index.values[i] > self.target_date and df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:
                    sell_date.append(df.index.values[i].strftime('%Y-%m-%d'))

            if len(buy_date)>0:
                KR_buy[mk.codes[code]]=buy_date
            if len(sell_date)>0:
                KR_sell[mk.codes[code]]=sell_date


        mk = Analyzer.MarketDB('global')
        for i,code in enumerate(mk.codes):

            buy_date = []
            sell_date = []
            df = mk.get_daily_price(code, '2019-01-01')

            df['MA20'] = df['close'].rolling(window=20).mean()
            df['stddev'] = df['close'].rolling(window=20).std()
            df['upper'] = df['MA20'] + (df['stddev'] * 2)
            df['lower'] = df['MA20'] - (df['stddev'] * 2)
            df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])

            df['II'] = (2*df['close']-df['high']-df['low'])/(df['high']-df['low'])*df['volume']
            df['IIP21'] = df['II'].rolling(window=21).sum()/df['volume'].rolling(window=21).sum()*100
            df = df.dropna()

            for i in range(0, len(df.close)):
                if df.index.values[i] > self.target_date and df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:
                    buy_date.append(df.index.values[i].strftime('%Y-%m-%d'))
                elif df.index.values[i] > self.target_date and df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:
                    sell_date.append(df.index.values[i].strftime('%Y-%m-%d'))

            if len(buy_date)>0:
                global_buy[code]=buy_date
            if len(sell_date)>0:
                global_sell[code]=sell_date

        return KR_buy, KR_sell, global_buy, global_sell

    def by_band_trend_following(self):
        KR_buy = {}
        KR_sell = {}
        global_buy = {}
        global_sell = {}

        mk = Analyzer.MarketDB('KR')
        for i,code in enumerate(mk.codes):

            buy_date = []
            sell_date = []
            df = mk.get_daily_price(code, '2019-01-01')

            df['MA20'] = df['close'].rolling(window=20).mean() 
            df['stddev'] = df['close'].rolling(window=20).std() 
            df['upper'] = df['MA20'] + (df['stddev'] * 2)
            df['lower'] = df['MA20'] - (df['stddev'] * 2)
            df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])
            df['TP'] = (df['high'] + df['low'] + df['close']) / 3
            df['PMF'] = 0
            df['NMF'] = 0

            for i in range(len(df.close)-1):
                if df.TP.values[i] < df.TP.values[i+1]:
                    df.PMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
                    df.NMF.values[i+1] = 0
                else:
                    df.NMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
                    df.PMF.values[i+1] = 0
            df['MFR'] = (df.PMF.rolling(window=10).sum() /
                df.NMF.rolling(window=10).sum())
            df['MFI10'] = 100 - 100 / (1 + df['MFR'])
            df = df[19:]

            for i in range(0, len(df.close)):
                if df.index.values[i] > self.target_date and df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:
                    buy_date.append(df.index.values[i].strftime('%Y-%m-%d'))
                elif df.index.values[i] > self.target_date and df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:
                    sell_date.append(df.index.values[i].strftime('%Y-%m-%d'))

            if len(buy_date)>0:
                KR_buy[mk.codes[code]]=buy_date
            if len(sell_date)>0:
                KR_sell[mk.codes[code]]=sell_date


        mk = Analyzer.MarketDB('global')
        for i,code in enumerate(mk.codes):

            buy_date = []
            sell_date = []
            df = mk.get_daily_price(code, '2019-01-01')

            df['MA20'] = df['close'].rolling(window=20).mean() 
            df['stddev'] = df['close'].rolling(window=20).std() 
            df['upper'] = df['MA20'] + (df['stddev'] * 2)
            df['lower'] = df['MA20'] - (df['stddev'] * 2)
            df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])
            df['TP'] = (df['high'] + df['low'] + df['close']) / 3
            df['PMF'] = 0
            df['NMF'] = 0

            for i in range(len(df.close)-1):
                if df.TP.values[i] < df.TP.values[i+1]:
                    df.PMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
                    df.NMF.values[i+1] = 0
                else:
                    df.NMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
                    df.PMF.values[i+1] = 0
            df['MFR'] = (df.PMF.rolling(window=10).sum() /
                df.NMF.rolling(window=10).sum())
            df['MFI10'] = 100 - 100 / (1 + df['MFR'])
            df = df[19:]

            for i in range(0, len(df.close)):
                if df.index.values[i] > self.target_date and df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:
                    buy_date.append(df.index.values[i].strftime('%Y-%m-%d'))
                elif df.index.values[i] > self.target_date and df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:
                    sell_date.append(df.index.values[i].strftime('%Y-%m-%d'))

            if len(buy_date)>0:
                global_buy[code]=buy_date
            if len(sell_date)>0:
                global_sell[code]=sell_date

        return KR_buy, KR_sell, global_buy, global_sell

    def by_triple_screen(self):
        KR_buy = {}
        KR_sell = {}
        global_buy = {}
        global_sell = {}

        mk = Analyzer.MarketDB('KR')
        for i,code in enumerate(mk.codes):

            buy_date = []
            sell_date = []
            df = mk.get_daily_price(code, '2019-01-01')

            ema60 = df.close.ewm(span=60).mean()
            ema130 = df.close.ewm(span=130).mean()
            macd = ema60 - ema130
            signal = macd.ewm(span=45).mean()
            macdhist = macd - signal
            df = df.assign(ema130=ema130, ema60=ema60, macd=macd, signal=signal, macdhist=macdhist).dropna()

            df['number'] = df.index.map(mdates.date2num)
            ohlc = df[['number','open','high','low','close']]

            ndays_high = df.high.rolling(window=14, min_periods=1).max()
            ndays_low = df.low.rolling(window=14, min_periods=1).min()

            fast_k = (df.close - ndays_low) / (ndays_high - ndays_low) * 100
            slow_d = fast_k.rolling(window=3).mean()
            df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()

            for i in range(0, len(df.close)):
                if df.index.values[i] > self.target_date and df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:
                    buy_date.append(df.index.values[i].strftime('%Y-%m-%d'))
                elif df.index.values[i] > self.target_date and df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:
                    sell_date.append(df.index.values[i].strftime('%Y-%m-%d'))

            if len(buy_date)>0:
                KR_buy[mk.codes[code]]=buy_date
            if len(sell_date)>0:
                KR_sell[mk.codes[code]]=sell_date


        mk = Analyzer.MarketDB('global')
        for i,code in enumerate(mk.codes):

            buy_date = []
            sell_date = []
            df = mk.get_daily_price(code, '2019-01-01')

            ema60 = df.close.ewm(span=60).mean()
            ema130 = df.close.ewm(span=130).mean()
            macd = ema60 - ema130
            signal = macd.ewm(span=45).mean()
            macdhist = macd - signal
            df = df.assign(ema130=ema130, ema60=ema60, macd=macd, signal=signal, macdhist=macdhist).dropna()

            df['number'] = df.index.map(mdates.date2num)
            ohlc = df[['number','open','high','low','close']]

            ndays_high = df.high.rolling(window=14, min_periods=1).max()
            ndays_low = df.low.rolling(window=14, min_periods=1).min()

            fast_k = (df.close - ndays_low) / (ndays_high - ndays_low) * 100
            slow_d = fast_k.rolling(window=3).mean()
            df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()

            for i in range(0, len(df.close)):
                if df.index.values[i] > self.target_date and df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:
                    buy_date.append(df.index.values[i].strftime('%Y-%m-%d'))
                elif df.index.values[i] > self.target_date and df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:
                    sell_date.append(df.index.values[i].strftime('%Y-%m-%d'))

            if len(buy_date)>0:
                global_buy[code]=buy_date
            if len(sell_date)>0:
                global_sell[code]=sell_date

        return KR_buy, KR_sell, global_buy, global_sell

if __name__=="__main__":
    MM = MakeMessage()
    res = MM.by_band_reversal()
    for item in res:
        print(item)
