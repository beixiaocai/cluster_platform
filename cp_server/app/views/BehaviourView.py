from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect


def index(request):
    context = {
        "settings": g_settings.data
    }
    
    nodes = NodeModel.objects.all().order_by('-id')
    context["nodes"] = nodes
    
    return render(request, 'app/behaviour/index.html', context)


def api_getList(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("BehaviourView.getList() params:%s" % str(params))
        
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
            
            result = send_command_to_node_sync(node_code, 'get_behavior_algorithms', {
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
                msg = result.get('msg', 'failed to get behavior algorithms')
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
        g_logger.info("BehaviourView.getInfo() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_behavior_algorithm_info', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', {})
            else:
                msg = result.get('msg', 'failed to get behavior algorithm info')
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
        g_logger.info("BehaviourView.openEdit() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'edit_behavior_algorithm', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to edit behavior algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("BehaviourView.openEdit() res:%s" % str(res))
    return f_responseJson(res)


def api_openDel(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("BehaviourView.openDel() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'del_behavior_algorithm', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', 'failed to delete behavior algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("BehaviourView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openAdd(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("BehaviourView.openAdd() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'add_behavior_algorithm', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', 'failed to add behavior algorithm')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("BehaviourView.openAdd() res:%s" % str(res))
    return f_responseJson(res)


def api_openEditContext(request):
    ret = False
    msg = "未知错误"
    data = {}
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("BehaviourView.openEditContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_behavior_algorithm_edit_context', {
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
    g_logger.info("BehaviourView.openEditContext() res:%s" % str(res))
    return f_responseJson(res)
