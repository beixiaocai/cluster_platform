from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect


def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    return render(request, 'app/audio/index.html', context)


def api_getNodeAudios(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("AudioView.getNodeAudios() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        page = params.get('p', 1)
        page_size = params.get('ps', 100)
        
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
                page_size = 100
            
            result = send_command_to_node_sync(node_code, 'get_audios', {
                'p': page,
                'ps': page_size
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
                pageData = result.get('pageData', {})
            else:
                msg = result.get('msg', 'failed to get audios')
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
        g_logger.info("AudioView.openAdd() params:%s" % str({k: v for k, v in params.items() if k != 'file_content'}))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        name = params.get('name', '').strip()
        remark = params.get('remark', '').strip()
        file_content = params.get('file_content', '').strip()
        file_name = params.get('file_name', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not name:
            msg = "名称不能为空"
        else:
            if not file_content:
                uploaded_file = request.FILES.get('file')
                if uploaded_file:
                    file_content = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    file_name = uploaded_file.name
            
            if not file_content:
                msg = "请上传音频文件"
            else:
                result = send_command_to_node_sync(node_code, 'add_audio', {
                    'code': code,
                    'name': name,
                    'remark': remark,
                    'file_content': file_content,
                    'file_name': file_name
                }, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '添加成功')
                else:
                    msg = result.get('msg', '添加失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AudioView.openAdd() res:%s" % str(res))
    return f_responseJson(res)


def api_openEdit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AudioView.openEdit() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'edit_audio', params, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "编辑成功"
            else:
                msg = result.get('msg', 'failed to edit audio')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AudioView.openEdit() res:%s" % str(res))
    return f_responseJson(res)


def api_openDel(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("AudioView.openDel() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'del_audio', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "删除成功"
            else:
                msg = result.get('msg', 'failed to delete audio')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("AudioView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openInfo(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("AudioView.openInfo() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_audio_info', {'code': code}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                info = result.get('info', {})
                
                if info.get('audio_path'):
                    info['audio_url'] = f"/storage/openAccess?filename={info['audio_path']}&node_code={node_code}"
            else:
                msg = result.get('msg', 'failed to get audio info')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    return f_responseJson(res)
