from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect


def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    return render(request, 'app/alarmInterface/index.html', context)


def api_getNodeAlarmInterfaces(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("AlarmInterfaceView.getNodeAlarmInterfaces() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        page = params.get('p', 1)
        page_size = params.get('ps', 10)
        
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
                page_size = 10
            
            result = send_command_to_node_sync(node_code, 'get_alarm_interfaces', {
                'p': page,
                'ps': page_size
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
                pageData = result.get('pageData', {})
            else:
                msg = result.get('msg', 'failed to get alarm interfaces')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData
    }
    return f_responseJson(res)


def api_openAdd(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlarmInterfaceView.openAdd() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'add_alarm_interface', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to add alarm interface')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AlarmInterfaceView.openAdd() res:%s" % str(res))
    return f_responseJson(res)


def api_openEdit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlarmInterfaceView.openEdit() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'edit_alarm_interface', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to edit alarm interface')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AlarmInterfaceView.openEdit() res:%s" % str(res))
    return f_responseJson(res)


def api_openDel(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlarmInterfaceView.openDel() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'del_alarm_interface', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to delete alarm interface')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AlarmInterfaceView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openInfo(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("AlarmInterfaceView.openInfo() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_alarm_interface_info', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                info = result.get('info', {})
            else:
                msg = result.get('msg', 'failed to get alarm interface info')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    return f_responseJson(res)


def test(request):
    """渲染报警存储测试页面（在iframe中加载）"""
    return render(request, 'app/alarmInterface/test.html', {})


def api_openTest(request):
    """报警存储测试：接收文件上传，转base64后通过WebSocket转发到节点执行测试"""
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlarmInterfaceView.openTest() params keys:%s" % str(list(params.keys())))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        enable_base64 = params.get('enable_base64', '0')
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            # 构建转发参数
            forward_params = {
                'code': code,
                'enable_base64': enable_base64
            }
            
            # 从 request.FILES 获取上传的图片，转为 base64
            image_file = request.FILES.get('image')
            if image_file:
                image_bytes = image_file.read()
                forward_params['image_base64'] = base64.b64encode(image_bytes).decode('utf-8')
                forward_params['image_filename'] = image_file.name
                g_logger.info("AlarmInterfaceView.openTest() image: %s, size: %d bytes" % (image_file.name, len(image_bytes)))
            
            # 从 request.FILES 获取上传的视频，转为 base64
            video_file = request.FILES.get('video')
            if video_file:
                video_bytes = video_file.read()
                forward_params['video_base64'] = base64.b64encode(video_bytes).decode('utf-8')
                forward_params['video_filename'] = video_file.name
                g_logger.info("AlarmInterfaceView.openTest() video: %s, size: %d bytes" % (video_file.name, len(video_bytes)))
            
            result = send_command_to_node_sync(node_code, 'test_alarm_interface', forward_params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
                info = result.get('info', {})
            else:
                msg = result.get('msg', 'failed to test alarm interface')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("AlarmInterfaceView.openTest() res code:%s msg:%s" % (res['code'], res['msg']))
    return f_responseJson(res)
