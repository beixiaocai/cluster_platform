from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.consumers.ClusterConsumer import send_command_to_node_sync

def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    
    nodes = NodeModel.objects.all().order_by('-id')
    context["nodes"] = nodes
    
    return render(request, 'app/stream/index.html', context)


def api_getNodeStreams(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'GET':
        node_code = request.GET.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_streams', timeout=10)
            if result.get('code') == 1000:
                data = result.get('data', [])
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to get streams')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_openStartPusher(request):
    ret = False
    msg = "未知错误"
    pusher_key = ""
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.openStartPusher() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        stream_app = params.get('stream_app', '').strip()
        stream_name = params.get('stream_name', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not stream_app or not stream_name:
            msg = "stream_app and stream_name are required"
        else:
            forward_result = send_command_to_node_sync(node_code, 'add_stream_proxy', {
                'app': stream_app,
                'name': stream_name
            }, timeout=30)
            
            if forward_result.get('code') != 1000:
                forward_msg = forward_result.get('msg', 'unknown error')
                g_logger.warning(f"StreamView.openStartPusher() add_stream_proxy failed: {forward_msg}")
            
            dst_stream_app = node_code
            dst_stream_name = f"{stream_app}-{stream_name}"
            
            pusher_params = {
                'stream_app': stream_app,
                'stream_name': stream_name,
                'dst_stream_app': dst_stream_app,
                'dst_stream_name': dst_stream_name,
                'dst_host': g_config.externalHost,
                'dst_rtsp_port': g_config.mediaRtspPort,
                'dst_http_port': g_config.mediaHttpPort,
                'dst_secret': g_config.mediaSecret
            }
            
            result = send_command_to_node_sync(node_code, 'add_stream_pusher', pusher_params, timeout=30)
            
            g_logger.info(f"StreamView.openStartPusher() result: {result}")
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data') or {}
                pusher_key = result.get('key', '') or data.get('key', '')
                g_logger.info(f"StreamView.openStartPusher() pusher_key: {pusher_key}")
            else:
                msg = result.get('msg', 'failed to start pusher')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "pusher_key": pusher_key
    }
    g_logger.info("StreamView.openStartPusher() res:%s" % str(res))
    return f_responseJson(res)


def api_openStopPusher(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.openStopPusher() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        pusher_key = params.get('pusher_key', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not pusher_key:
            msg = "pusher_key is required"
        else:
            pusher_params = {
                'key': pusher_key
            }
            
            result = send_command_to_node_sync(node_code, 'del_stream_pusher', pusher_params, timeout=10)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to stop pusher')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.openStopPusher() res:%s" % str(res))
    return f_responseJson(res)


def player(request):
    context = {
        "settings": f_settingsReadData()
    }
    params = f_parseGetParams(request)
    g_logger.debug("StreamView.player() params:%s" % str(params))
    
    node_code = params.get('node_code', '').strip()
    stream_app = params.get('app', '').strip()
    stream_name = params.get('name', '').strip()
    
    if node_code and stream_app and stream_name:
        app = node_code
        name = f"{stream_app}-{stream_name}"
        
        info = {
            "node_code": node_code,
            "stream_app": stream_app,
            "stream_name": stream_name,
            "wsMp4Url": g_zlm.get_wsMp4Url(app=app, name=name),
            "httpMp4Url": g_zlm.get_httpMp4Url(app=app, name=name),
            "rtspUrl": g_zlm.get_rtspUrl(app=app, name=name)
        }
        context["info"] = info
        g_logger.debug("StreamView.player() info:%s" % str(info))
        
        return render(request, 'app/stream/player.html', context)
    else:
        return redirect("/stream/index")
