from app.views.ViewsBase import *

g_logger.info("LLMView loaded")


def index(request):
    return render(request, 'app/llm/index.html', {"settings": g_settings.data})


def test(request):
    return render(request, 'app/llm/test.html', {"settings": g_settings.data})


def api_getList(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'get_llms', {}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    data = result.get('data', [])
                    msg = "获取成功"
                else:
                    msg = result.get('msg', '获取失败')
        except Exception as e:
            msg = f"获取失败：{str(e)}"
            g_logger.error(f"LLMView.api_getList() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_getTypes(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'get_llm_types', {}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    data = result.get('data', [])
                    msg = "获取成功"
                else:
                    msg = result.get('msg', '获取失败')
        except Exception as e:
            msg = f"获取失败：{str(e)}"
            g_logger.error(f"LLMView.api_getTypes() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_add(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                params = {
                    'code': request.POST.get('code', '').strip(),
                    'model_name': request.POST.get('model_name', '').strip(),
                    'inference_tool': request.POST.get('inference_tool', '').strip(),
                    'api_url': request.POST.get('api_url', '').strip(),
                    'api_key': request.POST.get('api_key', '').strip(),
                    'timeout': request.POST.get('timeout', '30').strip(),
                    'state': request.POST.get('state', '1').strip(),
                }
                
                result = send_command_to_node_sync(node_code, 'add_llm', params, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '添加成功')
                else:
                    msg = result.get('msg', '添加失败')
        except Exception as e:
            msg = f"添加失败：{str(e)}"
            g_logger.error(f"LLMView.api_add() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)


def api_edit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                params = {
                    'code': request.POST.get('code', '').strip(),
                    'model_name': request.POST.get('model_name', '').strip(),
                    'inference_tool': request.POST.get('inference_tool', '').strip(),
                    'api_url': request.POST.get('api_url', '').strip(),
                    'api_key': request.POST.get('api_key', '').strip(),
                    'timeout': request.POST.get('timeout', '30').strip(),
                    'state': request.POST.get('state', '1').strip(),
                }
                
                result = send_command_to_node_sync(node_code, 'edit_llm', params, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '编辑成功')
                else:
                    msg = result.get('msg', '编辑失败')
        except Exception as e:
            msg = f"编辑失败：{str(e)}"
            g_logger.error(f"LLMView.api_edit() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)


def api_del(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            llm_code = request.POST.get('id', '').strip()
            
            if not node_code:
                msg = "node_code is required"
            elif not llm_code:
                msg = "code is required"
            else:
                result = send_command_to_node_sync(node_code, 'del_llm', {'code': llm_code}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '删除成功')
                else:
                    msg = result.get('msg', '删除失败')
        except Exception as e:
            msg = f"删除失败：{str(e)}"
            g_logger.error(f"LLMView.api_del() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)


def api_getInfo(request):
    ret = False
    msg = "未知错误"
    data = {}
    
    if request.method == 'GET':
        try:
            node_code = request.GET.get('node_code', '').strip()
            llm_code = request.GET.get('code', '').strip()
            
            if not node_code:
                msg = "node_code is required"
            elif not llm_code:
                msg = "code is required"
            else:
                result = send_command_to_node_sync(node_code, 'get_llm_info', {'code': llm_code}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    data = result.get('info', result.get('data', {}))
                    msg = "获取成功"
                else:
                    msg = result.get('msg', '获取失败')
        except Exception as e:
            msg = f"获取失败：{str(e)}"
            g_logger.error(f"LLMView.api_getInfo() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_test(request):
    ret = False
    msg = "未知错误"
    data = {}
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            llm_code = request.POST.get('code', '').strip()
            prompt = request.POST.get('prompt', '').strip()
            
            if not node_code:
                msg = "node_code is required"
            elif not llm_code:
                msg = "code is required"
            elif not prompt:
                msg = "prompt is required"
            else:
                file = request.FILES.get('file')
                if not file:
                    msg = "file is required"
                else:
                    file_content = file.read()
                    file_content_base64 = base64.b64encode(file_content).decode('utf-8')
                    
                    params = {
                        'code': llm_code,
                        'prompt': prompt,
                        'file_content': file_content_base64,
                        'file_name': file.name
                    }
                    
                    result = send_command_to_node_sync(node_code, 'llm_test', params, timeout=120)
                    
                    if result.get('code') == 1000:
                        ret = True
                        data = {'content': result.get('result', '')}
                        msg = result.get('msg', '测试成功')
                    else:
                        msg = result.get('msg', '测试失败')
        except Exception as e:
            msg = f"测试失败：{str(e)}"
            g_logger.error(f"LLMView.api_test() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)
