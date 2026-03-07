import os
from app.models import *
from app.views.ViewsBase import *
from django.shortcuts import render


def api_getNodeList(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'GET':
        nodes = NodeModel.objects.all()
        for node in nodes:
            data.append({
                'code': node.code,
                'nickname': node.nickname or node.name or node.code,
                'host': node.host
            })
        ret = True
        msg = "success"
    else:
        msg = "request method not supported"
    
    res = {
        "code": 0 if ret else 1,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_getZlmProcessData(request):
    ret = False
    msg = "未知错误"
    info = {}
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            is_online = g_zlm.version()
            if is_online:
                media_data = g_zlm.getMediaList()
                total_media_count = len(media_data)
            else:
                total_media_count = 0

            info["process_state"] = 1 if is_online else 0
            info["total_media_count"] = total_media_count
            ret = True
            msg = "success"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    return f_responseJson(res)


