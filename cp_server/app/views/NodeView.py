import os
import time
from datetime import datetime

from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels, gen_random_code_s

def index(request):
    context = {
        "settings": f_settingsReadData()
    }

    data = []
    params = f_parseGetParams(request)

    page = params.get('p', 1)
    page_size = params.get('ps', 10)
    try:
        page = int(page)
    except:
        page = 1

    try:
        page_size = int(page_size)
        if page_size < 1:
            page_size = 1
    except:
        page_size = 10

    skip = (page - 1) * page_size
    
    nodes = NodeModel.objects.all().order_by('-id')[skip:skip+page_size]
    count = NodeModel.objects.count()

    data = []
    for node in nodes:
        node_dict = {
            'id': node.id,
            'code': node.code,
            'name': node.name,
            'nickname': node.nickname,
            'describe': node.describe,
            'system_name': node.system_name,
            'machine_node': node.machine_node,
            'host': node.host,
            'version': node.version,
            'flag': node.flag,
            'is_auth': node.is_auth,
            'is_multi_process': node.is_multi_process,
            'max_count': node.max_count,
            'ws_connected': node.ws_connected,
            'ws_channel': node.ws_channel,
            'ws_connect_time': node.ws_connect_time,
            'ws_last_heartbeat': node.ws_last_heartbeat,
            'create_time': node.create_time,
            'last_update_time': node.last_update_time,
        }
        
        online_node = get_node_manager().get_node(node.code)
        if online_node:
            node_dict['online'] = True
            node_dict['online_last_heartbeat'] = online_node.get('last_heartbeat')
        else:
            node_dict['online'] = False
        
        data.append(node_dict)

    page_num = int(count / page_size)
    if count % page_size > 0:
        page_num += 1
    pageLabels = buildPageLabels(page=page, page_num=page_num)
    pageData = {
        "page": page,
        "page_size": page_size,
        "page_num": page_num,
        "count": count,
        "pageLabels": pageLabels
    }

    context["data"] = data
    context["pageData"] = pageData
    return render(request, 'app/node/index.html', context)


def edit(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        handle = request.POST.get("handle", "")
        code = request.POST.get("code", "").strip()
        nickname = request.POST.get("nickname", "").strip()
        describe = request.POST.get("describe", "").strip()
        
        params = {
            "handle": handle,
            "code": code,
            "nickname": nickname,
            "describe": describe
        }
        g_logger.info("NodeView.edit() params:%s" % str(params))

        try:
            if handle != "edit":
                raise Exception("request parameters are incorrect")

            node = NodeModel.objects.filter(code=code).first()
            if node:
                node.nickname = nickname
                node.describe = describe
                node.last_update_time = datetime.now()
                node.save()

                __msg = "编辑成功"
                __ret = True
            else:
                __msg = "该节点不存在"
        except Exception as e:
            __msg = str(e)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            res = {
                "code": 1000 if __ret else 0,
                "msg": __msg
            }
            g_logger.info("NodeView.edit() ajax res:%s" % str(res))
            return f_responseJson(res)
        else:
            if __ret:
                redirect_url = "/node/index"
            else:
                redirect_url = "/node/edit?code=" + code
            g_logger.info("NodeView.edit() ret=%d,msg=%s" % (__ret, __msg))
            return render(request, 'app/message.html',
                          {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})

    else:
        context = {
            "settings": f_settingsReadData()
        }
        params = f_parseGetParams(request)
        code = params.get("code")
        if code:
            node = NodeModel.objects.filter(code=code).first()
            if node:
                context["handle"] = "edit"
                context["node"] = node
                return render(request, 'app/node/edit.html', context)
            else:
                return render(request, 'app/message.html',
                              {"msg": "该节点不存在", "is_success": False, "redirect_url": "/node/index"})
        else:
            return redirect("/node/index")


def api_openDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        code = request.POST.get("code")
        g_logger.info("NodeView.openDel() code:%s" % code)

        if code:
            node = NodeModel.objects.filter(code=code).first()
            if node:
                if node.delete():
                    ret = True
                    msg = "success"
                else:
                    msg = "failed to delete model"
            else:
                msg = "the data does not exist"
        else:
            msg = "code is required"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("NodeView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openNodeDetail(request):
    ret = False
    msg = "未知错误"
    data = {}
    if request.method == 'GET':
        code = request.GET.get('code', '')
        g_logger.info("NodeView.openNodeDetail() code:%s" % code)
        
        if code:
            node = NodeModel.objects.filter(code=code).first()
            if node:
                data = {
                    'id': node.id,
                    'code': node.code,
                    'name': node.name,
                    'nickname': node.nickname,
                    'describe': node.describe,
                    'system_name': node.system_name,
                    'machine_node': node.machine_node,
                    'host': node.host,
                    'version': node.version,
                    'flag': node.flag,
                    'is_auth': node.is_auth,
                    'is_multi_process': node.is_multi_process,
                    'max_count': node.max_count,
                    'ws_connected': node.ws_connected,
                    'ws_connect_time': node.ws_connect_time,
                    'ws_last_heartbeat': node.ws_last_heartbeat,
                }
                ret = True
                msg = "success"
            else:
                msg = "the data does not exist"
        else:
            msg = "code is required"
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info("NodeView.openNodeDetail() res:%s" % str(res))
    return f_responseJson(res)


def api_getOnlineNodes(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'GET':
        try:
            online_nodes = get_node_manager().get_connected_nodes()
            for node in online_nodes:
                data.append({
                    'code': node.get('code'),
                    'name': node.get('name'),
                    'host': node.get('host'),
                    'last_heartbeat': node.get('last_heartbeat').isoformat() if node.get('last_heartbeat') else None,
                })
            ret = True
            msg = "success"
        except Exception as e:
            msg = str(e)
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)
