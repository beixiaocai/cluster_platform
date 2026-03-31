from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect


def index(request):
    context = {
        "settings": g_settings.data
    }
    
    nodes = NodeModel.objects.all().order_by('-id')
    context["nodes"] = nodes
    
    return render(request, 'app/algorithm/index.html', context)


def api_getList(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("AlgorithmView.getList() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        page = params.get('p', 1)
        page_size = params.get('ps', 10)
        search_key = params.get('search', '').strip()
        
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
            
            result = send_command_to_node_sync(node_code, 'get_basic_algorithms', {
                'p': page,
                'ps': page_size,
                'search': search_key
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
                pageData = result.get('pageData', {})
                
                # 添加 ID 字段，使用索引作为临时 ID
                for i, item in enumerate(data):
                    if 'id' not in item:
                        item['id'] = i + 1
                
                # 按照 ID 倒序排序
                data.sort(key=lambda x: x.get('id', 0), reverse=True)
                
                # 根据搜索关键词过滤数据
                if search_key:
                    search_key = search_key.lower()
                    data = [item for item in data if 
                            (item.get('name', '').lower().find(search_key) != -1) or 
                            (item.get('code', '').lower().find(search_key) != -1)]
            else:
                msg = result.get('msg', 'failed to get basic algorithms')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData
    }
    return f_responseJson(res)


def api_getInfo(request):
    ret = False
    msg = "未知错误"
    data = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("AlgorithmView.getInfo() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_basic_algorithm_info', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', {})
            else:
                msg = result.get('msg', 'failed to get basic algorithm info')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_openEdit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlgorithmView.openEdit() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'edit_basic_algorithm', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to edit basic algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AlgorithmView.openEdit() res:%s" % str(res))
    return f_responseJson(res)


def api_openDel(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlgorithmView.openDel() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'del_basic_algorithm', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to delete basic algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AlgorithmView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openEditContext(request):
    ret = False
    msg = "未知错误"
    data = {}
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlgorithmView.openEditContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_basic_algorithm_edit_context', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', {})
            else:
                msg = result.get('msg', 'failed to get edit context')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info("AlgorithmView.openEditContext() res:%s" % str(res))
    return f_responseJson(res)


def api_openTypeAttrs(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("AlgorithmView.openTypeAttrs() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        algorithm_type_code = params.get('algorithm_type_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not algorithm_type_code:
            msg = "algorithm_type_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_basic_algorithm_type_attrs', {
                'algorithm_type_code': algorithm_type_code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                info = result.get('info', {})
            else:
                msg = result.get('msg', 'failed to get type attrs')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("AlgorithmView.openTypeAttrs() res:%s" % str(res))
    return f_responseJson(res)


def api_openAdd(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlgorithmView.openAdd() params keys:%s" % str(list(params.keys())))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            # 从 request.FILES 获取上传的模型文件，转为 base64 通过 WebSocket 传递
            model_file = request.FILES.get('model')
            if model_file:
                try:
                    file_bytes = model_file.read()
                    params['model_base64'] = base64.b64encode(file_bytes).decode('utf-8')
                    params['model_filename'] = model_file.name
                    g_logger.info("AlgorithmView.openAdd() file: %s, size: %d bytes" % (model_file.name, len(file_bytes)))
                except Exception as e:
                    g_logger.error("AlgorithmView.openAdd() read file error: %s" % str(e))
                    res = {"code": 0, "msg": "读取上传文件失败: " + str(e)}
                    return f_responseJson(res)
            
            # 转发到节点，包含base64文件数据，需要更长超时（大模型转换可能需要20分钟+）
            result = send_command_to_node_sync(node_code, 'add_basic_algorithm', params, timeout=1800)
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to add basic algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AlgorithmView.openAdd() res:%s" % str(res))
    return f_responseJson(res)


def api_openAddContext(request):
    ret = False
    msg = "未知错误"
    data = {}
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AlgorithmView.openAddContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_basic_algorithm_add_context', {}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', {})
            else:
                msg = result.get('msg', 'failed to get add context')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info("AlgorithmView.openAddContext() res:%s" % str(res))
    return f_responseJson(res)
