import json
from io import BytesIO
import re
import requests
from PIL import Image
from wechatpy.replies import ArticlesReply

baidu_img_url = "http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word={}"


# 获得页面第一张图片的链接
def get_pic_links(url):
    req = requests.get(url)
    html = req.text
    links = re.findall(r'"thumbURL":"(.*?.jpg)"', html)[0]  # 小图
    sourcelinks = re.findall(r'"objURL":"(.*?)"', html)[0]  # 原图
    return links, sourcelinks


def guess_flower(file, msg):
    img = Image.open(file)
    new_file = BytesIO()
    width, height = img.size

    if width > height:  # adjust size for best result
        delta = width - height
        left = int(delta / 2)
        upper = 0
        right = height + left
        lower = height
    else:
        delta = height - width
        left = 0
        upper = int(delta / 2)
        right = width
        lower = width + upper

    img = img.crop((left, upper, right, lower))
    img.save(new_file, "JPEG")
    new_file.seek(0, 0)
    multiple_files = [
        ('file1', ("xxx.jpg", new_file, 'image/jpeg'))]
    r = requests.post("http://stu.iplant.cn/upload.ashx", files=multiple_files)
    res = json.loads(r.text)
    base64_data = res['base64']
    url2 = "http://159.226.89.96:24606/plt5k"

    requests.options(url2)
    r2 = requests.post(url2, json={
        'deviceid': "stu",
        "image": base64_data,
    })
    result = json.loads(r2.text)
    flower_list = result['payload']['list']
    score1 = result['payload']['is_plant']

    returnd = ""

    reply = ArticlesReply(message=msg)

    if score1 < 0:  # 小于0说明是花的可能性很低很低。。
        pass
    else:
        guess_ke = flower_list[0]['family']  # 科
        guess_slhu = flower_list[0]['genus']  # 属

    for flow in flower_list:
        thumbURL, originURL = get_pic_links(baidu_img_url.format(flow['name'] + " 花"))
        reply.add_article({
            'title': '{0} (可信度{1:.2f}%)'.format(flow['name'], flow['score']),
            'description': '',
            'image': thumbURL,
            'url': 'http://baike.baidu.com/item/{0}'.format(flow['name'])
        })
    return reply


if __name__ == "__main__":
    with open("/Users/gaoliang/Desktop/2333.jpg", 'rb') as f:
        print(guess_flower(f))
