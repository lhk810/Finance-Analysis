import pandas as pd
import pymysql
from datetime import datetime
from datetime import timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import Analyzer

class DualMomentum:
    def __init__(self, target, delta):
        if target == 'KR':
            self.db = 'finance'
        elif target == 'global':
            self.db = 'finance_global'
        else :
            print("wrong argument for choosing DB")
            sys.exit()

        if delta is None:
            self.delta = 6*30
        else:
            self.delta = int(delta)*30

        pd.set_option("display.max_rows", None, "display.max_columns", 10, 'display.expand_frame_repr', False)

        self.mk = Analyzer.MarketDB(target)
    
    def get_rltv_momentum(self, start_date=None, end_date=None, stock_count=None):
        connection = pymysql.connect(host='localhost', db=self.db, user='hong', passwd='hong', autocommit=True)
        cursor = connection.cursor()

        #for handle defalut values:
        if start_date is None:
            start_date = ( datetime.today()-timedelta(days=self.delta) ).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = (datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')
        if stock_count is None:
            stock_count = len(self.mk.codes)
        
        sql = f"select max(date) from daily_price where date <= '{start_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print ("start_date : {} -> returned None".format(sql))
            return
        start_date = result[0].strftime('%Y-%m-%d')


        sql = f"select max(date) from daily_price where date <= '{end_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print ("end_date : {} -> returned None".format(sql))
            return
        end_date = result[0].strftime('%Y-%m-%d')

        rows = []
        columns = ['code', 'company', 'old_price', 'new_price', 'returns']
        for _, code in enumerate(self.mk.codes):            
            sql = f"select close from daily_price "\
                f"where code='{code}' and date='{start_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            old_price = int(result[0])
            sql = f"select close from daily_price "\
                f"where code='{code}' and date='{end_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            new_price = int(result[0])
            returns = (new_price / old_price - 1) * 100
            rows.append([code, self.mk.codes[code], old_price, new_price, 
                returns])

        df = pd.DataFrame(rows, columns=columns)
        df = df[['code', 'company', 'old_price', 'new_price', 'returns']]
        df = df.sort_values(by='returns', ascending=False)
        df = df.head(stock_count)
        df.index = pd.Index(range(stock_count))
        connection.close()
        print(df)
        print(f"\nRelative momentum ({start_date} ~ {end_date}) : "\
            f"{df['returns'].mean():.2f}% \n")
        return df
    
    def get_abs_momentum(self, rltv_momentum, start_date=None, end_date=None):
        stockList = list(rltv_momentum['code'])        
        connection = pymysql.connect(host='localhost', db=self.db, user='hong', passwd='hong', autocommit=True)
        cursor = connection.cursor()

        #for handle defalut values:
        if start_date is None:
            start_date = ( datetime.today()-timedelta(days=self.delta) ).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = ( datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')

        sql = f"select max(date) from daily_price "\
            f"where date <= '{start_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print ("{} -> returned None".format(sql))
            return
        start_date = result[0].strftime('%Y-%m-%d')

        sql = f"select max(date) from daily_price "\
            f"where date <= '{end_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print ("{} -> returned None".format(sql))
            return
        end_date = result[0].strftime('%Y-%m-%d')

        rows = []
        columns = ['code', 'company', 'old_price', 'new_price', 'returns']
        for _, code in enumerate(stockList):            
            sql = f"select close from daily_price "\
                f"where code='{code}' and date='{start_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            old_price = int(result[0])
            sql = f"select close from daily_price "\
                f"where code='{code}' and date='{end_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            new_price = int(result[0])
            returns = (new_price / old_price - 1) * 100
            rows.append([code, self.mk.codes[code], old_price, new_price,
                returns])


        # 절대 모멘텀 데이터프레임을 생성한 후 수익률순으로 출력
        df = pd.DataFrame(rows, columns=columns)
        df = df[['code', 'company', 'old_price', 'new_price', 'returns']]
        df = df.sort_values(by='returns', ascending=False)
        connection.close()
        print(df)
        print(f"\nAbasolute momentum ({start_date} ~ {end_date}) : "\
            f"{df['returns'].mean():.2f}%")
        return

if __name__=='main':
    if len(sys.argv) < 2:
        print("need arguments")
        sys.exit()
    if len(sys.argv) >= 2:
        target = sys.argv[1]
        delta = None
    if len(sys.argv) == 3:
        delta = sys.argv[2]
    dm = DualMomentum(target, delta)
    rm = dm.get_rltv_momentum()
    #am = dm.get_abs_momentum(rm)
