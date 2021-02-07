import pandas as pd
from bs4 import BeautifulSoup
import urllib, pymysql, calendar, time, json
from urllib.request import urlopen
from datetime import datetime
from threading import Timer
import pymysql
import requests

class DBUpdater:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='hong', password='hong', db='finance', charset='utf8')
        
        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE IF NOT EXISTS company_info (
                code VARCHAR(20),
                company VARCHAR(40),
                last_update DATE,
                PRIMARY KEY(code)
            )
            """
            curs.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS daily_price (
                code VARCHAR(20),
                date DATE,
                open BIGINT(20),
                high BIGINT(20),
                low BIGINT(20),
                close BIGINT(20),
                diff BIGINT(20),
                volume BIGINT(20),
                PRIMARY KEY (code, date)
            )
            """
            curs.execute(sql)
        self.conn.commit()
        self.codes = dict()
    
    def __del__(self):
        self.conn.close()

    def read_krx_code(self):
        target_file = "상장법인목록.xls"
        krx = pd.read_html(target_file)[0]
        krx = krx[['종목코드','회사명']]
        krx = krx.rename(columns={'종목코드':'code', '회사명':'company'})
        
        target_company = []
        try:
            with open('company_list', 'r', encoding='utf-8') as in_file:
                data = in_file.read().split('\n')
                for line in data:
                    target_company.append(line)
        except FileNotFoundError:
            target_company = ['삼성전자', 'NAVER', '카카오', '현대자동차']

        new_idx = 0
        index = []
        columns = ['code','company']
        rows = []
        
        for idx in range(len(krx)):
            if krx.company.values[idx] in target_company:
                index.append(new_idx)
                rows.append([krx.code.values[idx] ,krx.company.values[idx]])
                new_idx += 1
        res = pd.DataFrame(rows, columns=columns, index=index)

        res.code = res.code.map('{:06d}'.format)
        #print(res)
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
                krx = self.read_krx_code()
                for idx in range(len(krx)):
                    code = krx.code.values[idx]
                    company = krx.company.values[idx]
                    sql = f"REPLACE INTO company_info (code, company, last_update) VALUES ('{code}','{company}','{today}')"
                    curs.execute(sql)
                    self.codes[code] = company
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] #{idx+1:04d} REPLACE INTO company_infro VALUES ({code}, {company}, {today})")
                self.conn.commit()
                
    def read_naver(self, code, company, pages_to_fetch):
        try:
            url = f"http://finance.naver.com/item/sise_day.nhn?code={code}"
            with urlopen(url) as doc:
                if doc is None:
                    print('doc is None from read_naver()')
                    return None
                html = BeautifulSoup(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text, "lxml")
                pgrr = html.find("td", class_="pgRR")
                if pgrr is None:
                    print('pgrr is None from read_naver()')
                    return None
                s = str(pgrr.a["href"]).split('=')
                lastpage = s[-1]
            df = pd.DataFrame()
            pages = min(int(lastpage), pages_to_fetch)
            for page in range(1, pages+1):
                pg_url = '{}&page={}'.format(url, page)
                df = df.append(pd.read_html(requests.get(pg_url,headers={'User-agent': 'Mozilla/5.0'}).text)[0])
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                print('[{}] {} ({}) : {:04d}/{:04d} pages are downloading...'.format(tmnow, company, code, page, pages), end="\r")
            df = df.rename(columns={'날짜':'date','종가':'close','전일비':'diff','시가':'open','고가':'high','저가':'low','거래량':'volume'})
            df['date'] = df['date'].replace('.','-')
            df = df.dropna()
            df[['close','diff','open','high','low','volume']] = df[['close','diff','open','high','low','volume']].astype(int)
        except Exception as e:
            print('Exception occured : ',str(e))
            return None
        return df

    def replace_into_db(self, df, num, code, company):
        with self.conn.cursor() as curs:
            for r in df.itertuples():
                sql = "REPLACE INTO daily_price VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(code, r.date, r.open, r.high, r.low, r.close, r.diff, r.volume)
                curs.execute(sql)
            self.conn.commit()
            print("[{}] #{:04d} {} ({}) : {} rows > REPLACE_INTO daily_price [OK]".format(datetime.now().strftime('%Y-%m-%d %H:%M'), num+1, company, code, len(df)))

    def update_daily_price(self, pages_to_fetch):
        for idx,code in enumerate(self.codes):
            df = self.read_naver(code, self.codes[code], pages_to_fetch)
            if df is None:
                continue
            self.replace_into_db(df, idx, code, self.codes[code])

    def execute_daily(self):
        self.update_comp_info()
        try:
            with open('config.json', 'r') as in_file:
                config = json.load(in_file)
                pages_to_fetch = config['pages_to_fetch']
        except FileNotFoundError:
            with open('config.json', 'w') as out_file:
                pages_to_fetch = 100
                config = {'pages_to_fetch':1}
                json.dump(config, out_file)
        self.update_daily_price(pages_to_fetch)

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
