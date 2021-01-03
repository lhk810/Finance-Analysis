from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import mplfinance as mpf

url = 'https://www.tradingview.com/markets/stocks-usa/market-movers-large-cap/'
res = {}
with urlopen(url) as doc:
    html = BeautifulSoup(doc, 'lxml')
    table = html.find('table')
    rows = table.find_all('td')
    for td in rows:
        code = td.find('a')
        if not code is None and code.find('span') is None:
            key=code.text
            key=str(key)
            key = key.replace(".","-")
            key = key.replace("/","-")
            company = td.find('span', class_='tv-screener__description')
            company = company.text.strip()
            res[key]=company

with open('global_list','w') as out_file:
    for k,v in res.items():
        out_file.write('{}:{}'.format(k,v))
        out_file.write("\n")
    out_file.write("GC=F:Gold")
    out_file.write("\n")
    out_file.write("BTC-USD:Bitcoin USD")

