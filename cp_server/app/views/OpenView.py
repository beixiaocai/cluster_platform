import os
from app.models import *
from app.views.ViewsBase import *
from django.shortcuts import render


def api_getNodeList(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'GET':
        # 只获取在线的节点（内存中存在的节点）
        online_nodes = get_node_manager().get_connected_nodes()
        for node in online_nodes:
            data.append({
                'code': node.get('code'),
                'nickname': node.get('name') or node.get('code'),
                'host': node.get('host')
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


