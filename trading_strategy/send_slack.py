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

slack = Slacker(TOKEN_HERE)

sys.stdout = open('result/test.txt','w')

markdown_text = '*최근 6개월 상승률*\n'
print(markdown_text)
df = print_to_string(dual_momentum.DualMomentum('global',6).get_rltv_momentum())

slack.chat.post_message(channel=CHANNEL_HERE, text='FILE I/O TEST')
slack.files.upload('result/test.txt', channels=CHANNEL_HERE)
