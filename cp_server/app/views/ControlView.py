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
            }, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'get_control_context', {}, timeout=30)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                context = result.get('context', {})
                context["node_code"] = node_code
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
            result = send_command_to_node_sync(node_code, 'add_control', params, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'edit_control_context', {'code': code}, timeout=30)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                context = result.get('context', {})
                context["node_code"] = node_code
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
            result = send_command_to_node_sync(node_code, 'edit_control', params, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'del_control', {'code': code}, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'handle_control', handle_params, timeout=60)
            
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
            result = send_command_to_node_sync(node_code, 'get_control_log', log_params, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'add_control_algorithm', params, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'edit_control_algorithm', params, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'del_control_algorithm', {'code': code}, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'start_control_stream', {'code': code}, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'stop_control_stream', {'code': code}, timeout=30)
            
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
