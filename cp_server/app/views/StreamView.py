from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
import threading

def index(request):
    context = {
        "settings": g_settings.data
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
            result = send_command_to_node_sync(node_code, 'get_streams', timeout=120)
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


def api_openAddContext(request):
    ret = False
    msg = "未知错误"
    stream_info = {}
    pull_stream_types = []
    audio_types = []

    if request.method == 'GET':
        node_code = request.GET.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_stream_add_context', timeout=120)
            if result.get('code') == 1000:
                stream_info = result.get('stream', {})
                pull_stream_types = result.get('pull_stream_types', [])
                audio_types = result.get('audio_types', [])
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to get context')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "stream": stream_info,
        "pull_stream_types": pull_stream_types,
        "audio_types": audio_types
    }
    return f_responseJson(res)


def api_openAdd(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.api_openAdd() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            stream_params = {
                'code': params.get('code', '').strip(),
                'app': params.get('app', 'live').strip(),
                'name': params.get('name', '').strip(),
                'nickname': params.get('nickname', '').strip(),
                'pull_stream_type': int(params.get('pull_stream_type', 0)),
                'pull_stream_url': params.get('pull_stream_url', '').strip(),
                'pull_stream_ip': params.get('pull_stream_ip', '').strip(),
                'pull_stream_port': int(params.get('pull_stream_port', 0)),
                'camera_name': params.get('camera_name', '').strip(),
                'camera_manufacturer': params.get('camera_manufacturer', '').strip(),
                'camera_device_id': params.get('camera_device_id', '').strip(),
                'remark': params.get('remark', '').strip(),
                'onvif_username': params.get('onvif_username', '').strip(),
                'onvif_password': params.get('onvif_password', '').strip(),
                'is_audio': int(params.get('is_audio', 0))
            }
            
            result = send_command_to_node_sync(node_code, 'add_stream', stream_params, timeout=120)
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to add stream')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.api_openAdd() res:%s" % str(res))
    return f_responseJson(res)


def api_openEditContext(request):
    ret = False
    msg = "未知错误"
    stream_info = {}
    pull_stream_types = []
    audio_types = []

    if request.method == 'GET':
        node_code = request.GET.get('node_code', '').strip()
        stream_code = request.GET.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not stream_code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_stream_edit_context', {'code': stream_code}, timeout=120)
            if result.get('code') == 1000:
                stream_info = result.get('stream', {})
                pull_stream_types = result.get('pull_stream_types', [])
                audio_types = result.get('audio_types', [])
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to get context')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "stream": stream_info,
        "pull_stream_types": pull_stream_types,
        "audio_types": audio_types
    }
    return f_responseJson(res)


def api_openEdit(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.api_openEdit() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            stream_params = {
                'code': params.get('code', '').strip(),
                'nickname': params.get('nickname', '').strip(),
                'pull_stream_url': params.get('pull_stream_url', '').strip(),
                'pull_stream_ip': params.get('pull_stream_ip', '').strip(),
                'pull_stream_port': int(params.get('pull_stream_port', 0)),
                'camera_name': params.get('camera_name', '').strip(),
                'camera_manufacturer': params.get('camera_manufacturer', '').strip(),
                'camera_device_id': params.get('camera_device_id', '').strip(),
                'remark': params.get('remark', '').strip(),
                'is_audio': int(params.get('is_audio', 0))
            }
            
            result = send_command_to_node_sync(node_code, 'edit_stream', stream_params, timeout=120)
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to edit stream')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.api_openEdit() res:%s" % str(res))
    return f_responseJson(res)


def api_openDel(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.api_openDel() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        handle = params.get('handle', 'one')
        stream_code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            del_params = {
                'handle': handle,
                'code': stream_code
            }
            result = send_command_to_node_sync(node_code, 'del_stream', del_params, timeout=120)
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to delete stream')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.api_openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openAddStreamProxy(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.api_openAddStreamProxy() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        stream_code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not stream_code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'add_stream_proxy_by_code', {'code': stream_code}, timeout=120)
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to add stream proxy')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.api_openAddStreamProxy() res:%s" % str(res))
    return f_responseJson(res)


def api_openDelStreamProxy(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.api_openDelStreamProxy() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        stream_code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not stream_code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'del_stream_proxy_by_code', {'code': stream_code}, timeout=120)
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to delete stream proxy')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.api_openDelStreamProxy() res:%s" % str(res))
    return f_responseJson(res)


def api_openHandleAllStreamProxy(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.api_openHandleAllStreamProxy() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        handle = params.get('handle', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not handle:
            msg = "handle is required"
        else:
            result = send_command_to_node_sync(node_code, 'handle_all_stream_proxy', {'handle': handle}, timeout=120)
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to handle all stream proxy')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.api_openHandleAllStreamProxy() res:%s" % str(res))
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
            }, timeout=120)
            
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
            
            result = send_command_to_node_sync(node_code, 'add_stream_pusher', pusher_params, timeout=120)
            
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
            
            result = send_command_to_node_sync(node_code, 'del_stream_pusher', pusher_params, timeout=120)
            
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
        "settings": g_settings.data
    }
    params = f_parseGetParams(request)
    g_logger.debug("StreamView.player() params:%s" % str(params))
    
    node_code = params.get('node_code', '').strip()
    stream_app = params.get('app', '').strip()
    stream_name = params.get('name', '').strip()
    
    if node_code and stream_app and stream_name:
        app = node_code
        name = f"{stream_app}-{stream_name}"
        
        # 启动推流：将节点的流推送到 cp_server 的流媒体服务器
        def _push():
            try:
                send_command_to_node_sync(node_code, 'add_stream_proxy', {
                    'app': stream_app,
                    'name': stream_name
                }, timeout=120)
                pusher_params = {
                    'stream_app': stream_app,
                    'stream_name': stream_name,
                    'dst_stream_app': app,
                    'dst_stream_name': name,
                    'dst_host': g_config.externalHost,
                    'dst_rtsp_port': g_config.mediaRtspPort,
                    'dst_http_port': g_config.mediaHttpPort,
                    'dst_secret': g_config.mediaSecret
                }
                send_command_to_node_sync(node_code, 'add_stream_pusher', pusher_params, timeout=120)
            except Exception as e:
                g_logger.error(f"StreamView.player() push error: {e}")
        threading.Thread(target=_push, daemon=True).start()
        
        # 获取流的详细信息（包括 pull_stream_type）
        stream_info = {}
        try:
            result = send_command_to_node_sync(node_code, 'get_stream_by_app_name', {
                'app': stream_app,
                'name': stream_name
            }, timeout=120)
            g_logger.info(f"StreamView.player() get_stream result: {result}")
            if result.get('code') == 1000:
                stream_info = result.get('data', {})
                g_logger.info(f"StreamView.player() stream_info: {stream_info}")
        except Exception as e:
            g_logger.error(f"StreamView.player() get_stream error: {e}")
        
        info = {
            "node_code": node_code,
            "stream_app": stream_app,
            "stream_name": stream_name,
            "stream_code": stream_info.get('code', ''),
            "pull_stream_type": stream_info.get('pull_stream_type', 0),
            "wsMp4Url": g_zlm.get_wsMp4Url(app=app, name=name),
            "httpMp4Url": g_zlm.get_httpMp4Url(app=app, name=name),
            "rtspUrl": g_zlm.get_rtspUrl(app=app, name=name)
        }
        context["info"] = info
        g_logger.debug("StreamView.player() info:%s" % str(info))
        
        return render(request, 'app/stream/player.html', context)
    else:
        return redirect("/stream/index")


def api_openCheckDevice(request):
    ret = False
    msg = "未知错误"
    info = {}

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.api_openCheckDevice() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        ip = params.get('ip', '').strip()
        username = params.get('username', '').strip()
        password = params.get('password', '').strip()
        encrypted = params.get('encrypted', '1')
        
        if not node_code:
            msg = "node_code is required"
        elif not ip:
            msg = "请输入IP"
        elif not username:
            msg = "请输入用户名"
        elif not password:
            msg = "请输入密码"
        else:
            onvif_params = {
                'ip': ip,
                'username': username,
                'password': password,
                'encrypted': encrypted
            }
            result = send_command_to_node_sync(node_code, 'check_onvif_device', onvif_params, timeout=120)
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
                info = result.get('info', {})
            else:
                msg = result.get('msg', 'failed to check onvif device')
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("StreamView.api_openCheckDevice() res:%s" % str(res))
    return f_responseJson(res)


def api_openPtz(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamView.api_openPtz() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        ptzType = int(params.get('ptzType', 0))
        val = int(params.get('val', 0))
        
        if ptzType < 0 or ptzType > 11:
            msg = "ptzType must be 0-11"
        elif not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            ptz_params = {
                'code': code,
                'ptzType': ptzType,
                'val': val
            }
            result = send_command_to_node_sync(node_code, 'device_ptz', ptz_params, timeout=120)
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to control ptz')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("StreamView.api_openPtz() res:%s" % str(res))
    return f_responseJson(res)


def api_getAllStreamData(request):
    ret = False
    msg = "未知错误"
    data = []

    if request.method == "GET":
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.debug("StreamView.getAllStreamData() params=%s" % str(params))
            node_code = str(params.get('node_code', "")).strip()

            if not node_code:
                msg = "node_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'get_all_stream_data', {}, timeout=120)
                if result.get('code') == 1000:
                    ret = True
                    msg = "success"
                    data = result.get('data', [])
                else:
                    msg = result.get('msg', 'failed to get stream data')
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)
