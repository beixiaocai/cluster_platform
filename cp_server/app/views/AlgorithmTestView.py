from app.views.ViewsBase import *


def index(request):
    return render(request, 'app/algorithmTest/index.html', {"settings": g_settings.data})


def api_getFlows(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'get_algorithm_flows', {}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    data = result.get('data', [])
                    msg = "获取成功"
                else:
                    msg = result.get('msg', '获取失败')
        except Exception as e:
            msg = f"获取失败：{str(e)}"
            g_logger.error(f"AlgorithmTestView.api_getFlows() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_flowInit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            flow_code = request.POST.get('flow_code', '').strip()
            
            if not node_code:
                msg = "node_code is required"
            elif not flow_code:
                msg = "flow_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'flow_init', {'flowCode': flow_code}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '初始化成功')
                else:
                    msg = result.get('msg', '初始化失败')
        except Exception as e:
            msg = f"初始化失败：{str(e)}"
            g_logger.error(f"AlgorithmTestView.api_flowInit() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)


def api_flowRelease(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'flow_release', {}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '释放成功')
                else:
                    msg = result.get('msg', '释放失败')
        except Exception as e:
            msg = f"释放失败：{str(e)}"
            g_logger.error(f"AlgorithmTestView.api_flowRelease() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)


def api_flowAnalyze(request):
    ret = False
    msg = "未知错误"
    info = {}
    duration = 0
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            flow_code = request.POST.get('flow_code', '').strip()
            
            if not node_code:
                msg = "node_code is required"
            elif not flow_code:
                msg = "flow_code is required"
            else:
                file = request.FILES.get('file')
                if not file:
                    msg = "file is required"
                else:
                    file_content = file.read()
                    file_content_base64 = base64.b64encode(file_content).decode('utf-8')
                    
                    params = {
                        'flowCode': flow_code,
                        'file_content': file_content_base64,
                        'file_name': file.name
                    }

                    result = send_command_to_node_sync(node_code, 'flow_analyze', params, timeout=300)
                    
                    if result.get('code') == 1000:
                        ret = True
                        msg = result.get('msg', '计算完成')
                        info = result.get('info', {})
                        duration = result.get('duration', 0)
                    else:
                        msg = result.get('msg', '计算失败')
        except Exception as e:
            msg = f"计算失败：{str(e)}"
            g_logger.error(f"AlgorithmTestView.api_flowAnalyze() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info,
        "duration": duration
    }
    return f_responseJson(res)


def api_getImage(request):
    try:
        node_code = request.GET.get('node_code', '').strip()
        filename = request.GET.get('filename', '').strip()
        
        if not node_code or not filename:
            return f_responseJson({'code': 0, 'msg': 'Missing parameters'})
        
        result = send_command_to_node_sync(node_code, 'download_file', {
            'filename': filename
        }, timeout=120)
        
        if result.get('code') == 1000:
            file_content_base64 = result.get('data', {}).get('content', '')
            file_content = base64.b64decode(file_content_base64)
            
            http_response = HttpResponse(
                content=file_content,
                content_type='image/jpeg'
            )
            http_response['Content-Disposition'] = f'inline; filename="{filename}"'
            return http_response
        else:
            return f_responseJson({'code': 0, 'msg': result.get('msg', 'Download failed')})
            
    except Exception as e:
        g_logger.error(f"AlgorithmTestView.api_getImage() error: {str(e)}")
        return f_responseJson({'code': 0, 'msg': str(e)})
