from slacker import Slacker
import dual_momentum
import io
import sys
import pandas as pd

def print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

slack = Slacker(SOMETHING)

msg = '''
Fear & Greed
https://money.cnn.com/data/fear-and-greed/
'''

slack.chat.post_message(channel=CHANNEL, text=msg, unfurl_links='true', unfurl_media='true')

import make_slack_msg
MM = make_slack_msg.MakeMessage()

attach_list=[]
msg=''

KR_buy, KR_sell, global_buy, global_sell = MM.by_band_reversal()
msg += 'Long(Korea)\n'
for k,v in KR_buy.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Short(Korea)\n'
for k,v in KR_sell.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Long(gloal)\n'
for k,v in global_buy.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Short(global)\n'
for k,v in global_sell.items():
    msg += '    {} : {} \n'.format(k,v)

attach_dict = {
    'color' : '#ff0000',
    'title' : 'Result based on Bollinger band(reversal)',
    'text'  : msg,
    'mrkdwn': 'true'
}
attach_list.append(attach_dict)

msg=''
KR_buy, KR_sell, global_buy, global_sell = MM.by_band_trend_following()
msg += 'Long(Korea)\n'
for k,v in KR_buy.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Short(Korea)\n'
for k,v in KR_sell.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Long(gloal)\n'
for k,v in global_buy.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Short(global)\n'
for k,v in global_sell.items():
    msg += '    {} : {} \n'.format(k,v)

attach_dict = {
    'color' : '#00ff00',
    'title' : 'Result based on Bollinger band(trend following)',
    'text'  : msg,
    'mrkdwn': 'true'
}
attach_list.append(attach_dict)

msg=''
KR_buy, KR_sell, global_buy, global_sell = MM.by_triple_screen()
msg += 'Long(Korea)\n'
for k,v in KR_buy.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Short(Korea)\n'
for k,v in KR_sell.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Long(gloal)\n'
for k,v in global_buy.items():
    msg += '    {} : {} \n'.format(k,v)
msg += 'Short(global)\n'
for k,v in global_sell.items():
    msg += '    {} : {} \n'.format(k,v)

attach_dict = {
    'color' : '#0000ff',
    'title' : 'Result based on Triple Screen',
    'text'  : msg,
    'mrkdwn': 'true'
}
attach_list.append(attach_dict)

#print(msg)

slack.chat.post_message(channel=CHANNEL, text='Analysis & Signal for a week', attachments=attach_list)

#slack.files.upload('result/testfig.png',channels='돈벌시간')
#날짜 안맞는 문제 해결 후 사용
'''
sys.stdout = open('result/test.txt','w')
markdown_text = '*최근 6개월 상승률*\n'
print(markdown_text)
df = print_to_string(dual_momentum.DualMomentum('global',6).get_rltv_momentum())
slack.files.upload('result/test.txt', channels='#돈벌시간')
'''
