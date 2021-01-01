import requests

url = "https://www.musickorea.com/storage/woo680821EN/www/prefix/product/2015/43/O/product.5313.144551354844622.png"
r = requests.get(url, stream=True).raw

from PIL import Image

img = Image.open(r)
img.save('red_flag.png')

BUF_SIZE = 1024
with open('red_flag.png','rb') as sf, open ('dst.png','wb') as df:
    while True:
        data = sf.read(BUF_SIZE)
        if not data:
            break
        df.write(data)
