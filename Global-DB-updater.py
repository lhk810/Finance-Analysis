import pandas as pd
from pandas_datareader import data as pdr
import pymysql, calendar, time, json
from datetime import datetime
from threading import Timer
import pymysql
import sys
import yfinance

class DBUpdater:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='hong', password='hong', db='finance_global', charset='utf8')
        
        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE IF NOT EXISTS company_info (
                code VARCHAR(20),
                company VARCHAR(100),
                last_update DATE,
                PRIMARY KEY(code)
            )
            """
            curs.execute(sql)
            
            #no diff
            #BIGINT -> DOUBLE
            sql = """
            CREATE TABLE IF NOT EXISTS daily_price (
                code VARCHAR(20),
                date DATE,
                open DOUBLE(40,10),
                high DOUBLE(40,10),
                low DOUBLE(40,10),
                close DOUBLE(40,10),
                volume DOUBLE(40,10),
                PRIMARY KEY (code, date)
            )
            """
            curs.execute(sql)
        self.conn.commit()
        self.codes = dict()
    
    def __del__(self):
        self.conn.close()

    def read_global_code(self):
        target_company = []
        try:
            with open('global_list', 'r') as in_file:
                data = in_file.read().split('\n')
                for line in data:
                    if line != '':
                        target_company.append(line)
        except FileNotFoundError:
            print('Need global list! Exit the program!')
            sys.exit()

        new_idx = 0
        index = []
        columns = ['code','company']
        rows = []

        print(target_company)

        for item in target_company:
            code = item.split(':')[0]
            company = item.split(':')[1]
            row = [code, company]
            rows.append(row)
            index.append(new_idx)
            new_idx+=1

        res = pd.DataFrame(rows, columns=columns, index=index)

        return res

    def update_comp_info(self):
        sql = "SELECT * FROM company_info"
        df = pd.read_sql(sql, self.conn)
        for idx in range(len(df)):
            self.codes[df['code'].values[idx]] = df['company'].values[idx]

        with self.conn.cursor() as curs:
            sql = "SELECT max(last_update) FROM company_info"
            curs.execute(sql)
            rs = curs.fetchone()
            today = datetime.today().strftime('%Y-%m-%d')

            if rs[0]==None or rs[0].strftime('%Y-%m-%d') < today:
                print("Read company list...")
                krx = self.read_global_code()
                for idx in range(len(krx)):
                    code = krx.code.values[idx]
                    company = krx.company.values[idx]
                    sql = "REPLACE INTO company_info (code, company, last_update) VALUES ({},{},{})".format(json.dumps(code),json.dumps(company),json.dumps(today))
                    curs.execute(sql)
                    self.codes[code] = company
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] #{idx+1:04d} REPLACE INTO company_infro VALUES ({code}, {company}, {today})")
                self.conn.commit()
 
    def get_stock(self, name, start, end):
        nums = start.split('-')
        nums = list(map(int, nums))
        start = datetime(nums[0],nums[1],nums[2])
        nums = end.split('-')
        nums = list(map(int,nums))
        end = datetime(nums[0],nums[1],nums[2])
        return pdr.DataReader(name, 'yahoo', start, end)

    def read_yahoo(self, code, company, start_date):
        end_date = datetime.now().strftime('%Y-%m-%d')
        print("waiting for {} data...".format(company))
        df = self.get_stock(code, start_date, end_date)
        print("{} data downloaded".format(company))
        df['Date'] = df.index
        df = df[['Date','Close','Open','High','Low','Volume']]
        df = df.rename(columns={'Date':'date','Close':'close','Open':'open','High':'high','Low':'low','Volume':'volume'})
        df['date'] = df['date'].replace('.','-')
        df = df.dropna()
        df[['close','open','high','low','volume']] = df[['close','open','high','low','volume']].astype(float)
        return df

    def replace_into_db(self, df, num, code, company):
        with self.conn.cursor() as curs:
            for r in df.itertuples():
                sql = "REPLACE INTO daily_price VALUES ('{}', '{}', '{}', '{}', '{}', '{}',  '{}')".format(code, r.date, r.open, r.high, r.low, r.close, r.volume)
                curs.execute(sql)
            self.conn.commit()
            print("[{}] #{:04d} {} ({}) : {} rows > REPLACE_INTO daily_price [OK]".format(datetime.now().strftime('%Y-%m-%d %H:%M'), num+1, company, code, len(df)))

    def update_daily_price(self, start_date):
        for idx,code in enumerate(self.codes):
            df = self.read_yahoo(code, self.codes[code], start_date)
            if df is None:
                continue
            self.replace_into_db(df, idx, code, self.codes[code])

    def execute_daily(self):
        self.update_comp_info()
        try:
            with open('config_global.json', 'r') as in_file:
                config = json.load(in_file)
                start_date = config['start_date']
        except FileNotFoundError:
            with open('config_global.json', 'w') as out_file:
                start_date = '2016-01-01'
                config = {'start_date':'2021-01-01'}
                json.dump(config, out_file)
        self.update_daily_price(start_date)

        tmnow = datetime.now()
        lastday = calendar.monthrange(tmnow.year, tmnow.month)[1]
        if tmnow.month == 12 and tmnow.day == lastday:
            tmnext = tmnow.replace(year==tmnow.year+1, month=1, day=1, hour=17, minute=0, second=0)
        elif tmnow.day == lastday:
            tmnext = tmnow.replace(month==tmnow.month+1, day=1, hour=17, minute=0, second=0)
        else:
            tmnext = tmnow.replace(day=tmnow.day+1, hour=17, minute=0, second=0)
        tmdiff = tmnext - tmnow
        secs = tmdiff.seconds
        t = Timer(secs, self.execute_daily)
        print("Waiting for next update ({}) ...".format(tmnext.strftime('%Y-%m-%d %H:%M')))
        t.start()

if __name__ == '__main__':
    dbu = DBUpdater()
    dbu.execute_daily()
