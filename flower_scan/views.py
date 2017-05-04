from io import BytesIO

import requests
from PIL import Image
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

# disable csrf protection for this view
from django.views.decorators.csrf import csrf_exempt
from wechatpy.crypto import WeChatCrypto
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.exceptions import InvalidAppIdException

from django.conf import settings

from flower_scan.scan import guess_flower

TOKEN = ""
EncodingAESKey = ""
AppId = ""


# Create your views here.
def index(request):
    return HttpResponse("Wechat index.")


# use csrf_exempt to disable csrf protection for this view
@csrf_exempt
def scan(request):
    signature = request.GET.get('signature', '') + request.POST.get('signature', '')
    timestamp = request.GET.get('timestamp', '') + request.POST.get('timestamp', '')
    nonce = request.GET.get('nonce', '') + request.POST.get('nonce', '')
    echo_str = request.GET.get('echostr', '') + request.POST.get('echostr', '')
    encrypt_type = request.GET.get('encrypt_type', '') + request.POST.get('encrypt_type', '')
    msg_signature = request.GET.get('msg_signature', '') + request.POST.get('msg_signature', '')
    try:
        check_signature(TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        raise PermissionDenied
    if request.method == 'GET':
        return HttpResponse(echo_str)
    else:
        crypto = WeChatCrypto(TOKEN, EncodingAESKey, AppId)
        try:
            msg = crypto.decrypt_message(
                request.body,
                msg_signature,
                timestamp,
                nonce
            )
            print('Descypted message: \n%s' % msg)
        except (InvalidSignatureException, InvalidAppIdException):
            raise PermissionDenied
        msg = parse_message(msg)
        if msg.type == 'text':
            reply = create_reply("", msg)
        elif msg.type == 'image':
            file_formate = msg.image.split('/')[3].split('_')[-1]
            file = BytesIO(requests.get(msg.image).content)
            if file_formate == "png":
                im = Image.open(file)
                im.save(file, 'JPEG')
            reply = guess_flower(file, msg)

        elif msg.type == "event":
            if msg.event == "subscribe":
                reply = create_reply("感谢关注！", msg)
            elif msg.event == "click":
                if msg.key == "scan_flower":
                    reply = create_reply("直接把花的图片发给我就好啦！注意尽量保持花朵在图片的中间位置", msg)
                else:
                    print(msg.id)
                    reply = create_reply("", msg)
            else:
                reply = create_reply("", msg)
        else:
            reply = create_reply("暂不支持此种消息", msg)
        return HttpResponse(crypto.encrypt_message(
            reply.render(),
            nonce,
            timestamp
        ))
