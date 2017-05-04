from wechatpy import WeChatClient

from flower_scan.views import AppId

AppSecert = ""

client = WeChatClient(AppId, AppSecert)
client.menu.create({
    "button": [
        {
            "type": "click",
            "name": "扫描识花",
            "key": "scan_flower"
        },
    ]
})
