#윈도우 환경에서 실행
from pywinauto import application
import time
import os

os.system('taskkill /IM coStarter* /F /T')
os.system('taskkill /IM CpStart* /F /T')
os.system('wmic process where "name like \'%coStarter%\'" call terminate')
os.system('wmic process where "name like \'%CpStart%\'" call terminate')
time.sleep(5)        

app = application.Application()
with open('login','r') as file:
    read = file.read().split('\n')
    id = read[0]
    pwd = read[1]
    pwdcert = read[2]
connect_str = 'C:\CREON\STARTER\coStarter.exe /prj:cp /id:{id} /pwd:{pwd} /pwdcert:{pwdcert} /autostart'.format_map({'id':id, 'pwd':pwd,'pwdcert':pwdcert})
print(connect_str)
app.start(connect_str)
time.sleep(60)
