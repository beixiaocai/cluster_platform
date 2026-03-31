from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
import threading


def _get_cp_wsMp4Url(node_code, stream_app, stream_name):
    """生成 cp_server 代理的视频流播放地址"""
    cp_app = node_code
    cp_name = f"{stream_app}-{stream_name}"
    return g_zlm.get_wsMp4Url(app=cp_app, name=cp_name)


def _start_stream_push_to_cp(node_code, stream_app, stream_name):
    """异步启动流推送：从节点推流到 cp_server 的流媒体服务器"""
    def _push():
        try:
            send_command_to_node_sync(node_code, 'add_stream_proxy', {
                'app': stream_app,
                'name': stream_name
            }, timeout=120)
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
            send_command_to_node_sync(node_code, 'add_stream_pusher', pusher_params, timeout=120)
        except Exception as e:
            g_logger.error(f"_start_stream_push_to_cp error: {e}")
    threading.Thread(target=_push, daemon=True).start()


def _transform_stream_urls(node_code, stream_dict):
    """将节点返回的流数据中的 URL 替换为 cp_server 代理地址"""
    s_app = stream_dict.get('app', '')
    s_name = stream_dict.get('name', '')
    if s_app and s_name:
        cp_url = _get_cp_wsMp4Url(node_code, s_app, s_name)
        stream_dict['wsMp4Url'] = cp_url
        stream_dict['videoUrl'] = cp_url
        stream_dict['wsHost'] = g_zlm.get_wsHost()
        cp_app = node_code
        cp_name = f"{s_app}-{s_name}"
        stream_dict['httpMp4Url'] = g_zlm.get_httpMp4Url(app=cp_app, name=cp_name)
        stream_dict['rtspUrl'] = g_zlm.get_rtspUrl(app=cp_app, name=cp_name)
        stream_dict['wsFlvUrl'] = g_zlm.get_wsFlvUrl(app=cp_app, name=cp_name)
        stream_dict['httpFlvUrl'] = g_zlm.get_httpFlvUrl(app=cp_app, name=cp_name)


def index(request):
    context = {
        "settings": g_settings.data
    }
    
    nodes = NodeModel.objects.all().order_by('-id')
    context["nodes"] = nodes
    
    return render(request, 'app/control/index.html', context)


def api_getNodeControls(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ControlView.getNodeControls() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        page = params.get('p', 1)
        page_size = params.get('ps', 12)
        search_text = params.get('search_text', '').strip()
        search_status = params.get('search_status', '-1').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            try:
                page = int(page)
            except:
                page = 1
            try:
                page_size = int(page_size)
            except:
                page_size = 12
            
            result = send_command_to_node_sync(node_code, 'get_controls', {
                'p': page,
                'ps': page_size,
                'search_text': search_text,
                'search_status': search_status
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
                pageData = result.get('pageData', {})
            else:
                msg = result.get('msg', 'failed to get controls')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData
    }
    return f_responseJson(res)


def api_openAddContext(request):
    ret = False
    msg = "未知错误"
    context = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ControlView.openAddContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_control_context', {}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                context = result.get('context', {})
                context["node_code"] = node_code
                # 替换视频流地址为 cp_server 代理地址
                for stream in context.get('streams', []):
                    _transform_stream_urls(node_code, stream)
            else:
                msg = result.get('msg', 'failed to get context')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "context": context
    }
    return f_responseJson(res)


def api_openAdd(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openAdd() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'add_control', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to add control')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openAdd() res:%s" % str(res))
    return f_responseJson(res)


def api_openEditContext(request):
    ret = False
    msg = "未知错误"
    context = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ControlView.openEditContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'edit_control_context', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                context = result.get('context', {})
                context["node_code"] = node_code
                # 替换视频流地址为 cp_server 代理地址，并启动推流
                ctrl_stream = context.get('control_stream', {})
                if ctrl_stream:
                    _transform_stream_urls(node_code, ctrl_stream)
                    s_app = ctrl_stream.get('app', '')
                    s_name = ctrl_stream.get('name', '')
                    if s_app and s_name:
                        _start_stream_push_to_cp(node_code, s_app, s_name)
            else:
                msg = result.get('msg', 'failed to get context')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "context": context
    }
    return f_responseJson(res)


def api_openEdit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openEdit() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'edit_control', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to edit control')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openEdit() res:%s" % str(res))
    return f_responseJson(res)


def api_openDel(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openDel() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'del_control', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to delete control')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openHandle(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openHandle() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        handle = params.get('handle', '').strip()
        code = params.get('code', '').strip()
        state = params.get('state', 10)
        
        if not node_code:
            msg = "node_code is required"
        elif not handle:
            msg = "handle is required"
        else:
            handle_params = {
                'handle': handle,
                'code': code,
                'state': state
            }
            result = send_command_to_node_sync(node_code, 'handle_control', handle_params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to handle control')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openHandle() res:%s" % str(res))
    return f_responseJson(res)


def api_openLog(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ControlView.openLog() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        control_code = params.get('controlCode', '').strip()
        page = params.get('p', 1)
        page_size = params.get('ps', 20)
        
        if not node_code:
            msg = "node_code is required"
        else:
            log_params = {
                'controlCode': control_code,
                'p': page,
                'ps': page_size
            }
            result = send_command_to_node_sync(node_code, 'get_control_log', log_params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
            else:
                msg = result.get('msg', 'failed to get log')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info("ControlView.openLog() res:%s" % str(res))
    return f_responseJson(res)


def api_openAddAlgorithm(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openAddAlgorithm() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'add_control_algorithm', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to add algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openAddAlgorithm() res:%s" % str(res))
    return f_responseJson(res)


def api_openEditAlgorithm(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openEditAlgorithm() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'edit_control_algorithm', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to edit algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openEditAlgorithm() res:%s" % str(res))
    return f_responseJson(res)


def api_openDelAlgorithm(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openDelAlgorithm() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'del_control_algorithm', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to delete algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openDelAlgorithm() res:%s" % str(res))
    return f_responseJson(res)


def api_openStartControlStream(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openStartControlStream() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'start_control_stream', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to start control stream')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openStartControlStream() res:%s" % str(res))
    return f_responseJson(res)


def api_openStopControlStream(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openStopControlStream() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'stop_control_stream', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to stop control stream')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openStopControlStream() res:%s" % str(res))
    return f_responseJson(res)


def control_algorithm_add(request):
    context = {}
    
    params = f_parseGetParams(request)
    controlCode = params.get("controlCode", "").strip()
    node_code = params.get("node_code", "").strip()
    
    context["handle"] = "add"
    context["node_code"] = node_code
    context["control_code"] = controlCode
    
    if node_code and controlCode:
        result = send_command_to_node_sync(node_code, 'get_algorithm_flows', {}, timeout=120)
        if result.get('code') == 1000:
            context["flows"] = result.get('data', [])
        
        result = send_command_to_node_sync(node_code, 'get_llms', {}, timeout=120)
        if result.get('code') == 1000:
            context["llms"] = result.get('data', [])
        
        result = send_command_to_node_sync(node_code, 'get_control_info', {'code': controlCode}, timeout=120)
        if result.get('code') == 1000:
            context["control_info"] = result.get('info', {})
    
    import random
    import string
    random_part = ''.join(random.choices(string.digits, k=6))
    algo_code = "ca" + random_part
    context["algorithm_code"] = algo_code
    context["controlAlgorithm"] = {
        "code": algo_code,
        "control_code": controlCode,
    }
    
    return render(request, 'app/controlAlgorithm/add.html', context)


def api_openCopy(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openCopy() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        controlCode = params.get('controlCode', '').strip()
        streamCodes = params.get('streamCodes', '').strip()
        remark = params.get('remark', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not controlCode or not streamCodes:
            msg = "request parameters are incorrect"
        else:
            result = send_command_to_node_sync(node_code, 'copy_control', {
                'controlCode': controlCode,
                'streamCodes': streamCodes,
                'remark': remark
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to copy control')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openCopy() res:%s" % str(res))
    return f_responseJson(res)


def api_openSettings(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ControlView.openSettings() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        min_interval = params.get('min_interval', '0').strip()
        osd_params = params.get('osd_params', '').strip()
        extend_params = params.get('extend_params', '').strip()
        modify_range = params.get('modify_range', '0').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'settings_control', {
                'code': code,
                'min_interval': min_interval,
                'osd_params': osd_params,
                'extend_params': extend_params,
                'modify_range': modify_range
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to update settings')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ControlView.openSettings() res:%s" % str(res))
    return f_responseJson(res)


def api_openInfo(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ControlView.openInfo() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_control_info', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                info = result.get('info', {})
            else:
                msg = result.get('msg', 'failed to get control info')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("ControlView.openInfo() res:%s" % str(res))
    return f_responseJson(res)


def api_getControlInfo(request):
    ret = False
    msg = "未知错误"
    data = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_control_info', {'code': code}, timeout=120)
            if result.get('code') == 1000:
                ctrl_data = result.get('info', {})
                stream_app = ctrl_data.get('stream_app', '')
                stream_name = ctrl_data.get('stream_name', '')
                if stream_app and stream_name:
                    # 使用 cp_server 代理地址并启动推流
                    wsMp4Url = _get_cp_wsMp4Url(node_code, stream_app, stream_name)
                    _start_stream_push_to_cp(node_code, stream_app, stream_name)
                    data = {
                        'code': code,
                        'stream_app': stream_app,
                        'stream_name': stream_name,
                        'wsMp4Url': wsMp4Url
                    }
                    ret = True
                    msg = "success"
                else:
                    msg = "stream info not found"
            else:
                msg = result.get('msg', 'failed to get control info')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def control_algorithm_edit(request):
    context = {}
    
    params = f_parseGetParams(request)
    code = params.get("code", "").strip()
    node_code = params.get("node_code", "").strip()
    
    context["handle"] = "edit"
    context["node_code"] = node_code
    context["code"] = code
    context["control_code"] = ""
    context["algorithm_code"] = code
    context["controlAlgorithm"] = {}
    context["flows"] = []
    context["llms"] = []
    
    try:
        # 通过 WebSocket 从节点获取布控算法数据
        result = send_command_to_node_sync(node_code, 'get_control_algorithm_info', {'code': code}, timeout=120)
        if result.get('code') == 1000:
            algo_data = result.get('data', {})
            if algo_data:
                controlAlgorithm = {
                    "code": algo_data.get("code", ""),
                    "control_code": algo_data.get("control_code", ""),
                    "flow_code": algo_data.get("flow_code", ""),
                    "llm_code": algo_data.get("llm_code", ""),
                    "llm_prompt": algo_data.get("llm_prompt", ""),
                    "llm_happen_words": algo_data.get("llm_happen_words", ""),
                    "polygon": algo_data.get("polygon", ""),
                    "polygon_type": algo_data.get("polygon_type", 0),
                }
                context["controlAlgorithm"] = controlAlgorithm
                context["control_code"] = algo_data.get("control_code", "")
                
                # 如果节点返回了关联的布控信息（stream_app, stream_name）
                if algo_data.get("stream_app") and algo_data.get("stream_name"):
                    context["control_info"] = {
                        "code": algo_data.get("control_code", ""),
                        "stream_app": algo_data.get("stream_app", ""),
                        "stream_name": algo_data.get("stream_name", ""),
                    }
                else:
                    # 如果节点没返回 stream 信息，单独获取布控信息
                    controlCode = algo_data.get("control_code", "")
                    if controlCode:
                        ctrl_result = send_command_to_node_sync(node_code, 'get_control_info', {'code': controlCode}, timeout=120)
                        if ctrl_result.get('code') == 1000:
                            ctrl_data = ctrl_result.get('info', {})
                            context["control_info"] = {
                                "code": ctrl_data.get("code", controlCode),
                                "stream_app": ctrl_data.get("stream_app", ""),
                                "stream_name": ctrl_data.get("stream_name", ""),
                            }
        else:
            g_logger.error("control_algorithm_edit get_control_algorithm_info failed: %s" % result.get('msg', ''))
    except Exception as e:
        g_logger.error("control_algorithm_edit error: %s" % str(e))
    
    result = send_command_to_node_sync(node_code, 'get_algorithm_flows', {}, timeout=120)
    if result.get('code') == 1000:
        context["flows"] = result.get('data', [])
    
    result = send_command_to_node_sync(node_code, 'get_llms', {}, timeout=120)
    if result.get('code') == 1000:
        context["llms"] = result.get('data', [])
    
    g_logger.info("control_algorithm_edit context controlAlgorithm: %s" % str(context.get("controlAlgorithm")))
    
    return render(request, 'app/controlAlgorithm/add.html', context)
