from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect


def index(request):
    context = {
        "settings": g_settings.data
    }
    return render(request, 'app/face/index.html', context)


def api_getNodeFaces(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("FaceView.getNodeFaces() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        page = params.get('p', 1)
        page_size = params.get('ps', 10)
        search_text = params.get('search_text', '').strip()
        
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
            
            result = send_command_to_node_sync(node_code, 'get_faces', {
                'p': page,
                'ps': page_size,
                'search_text': search_text
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
                pageData = result.get('pageData', {})
            else:
                msg = result.get('msg', 'failed to get faces')
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
    info = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("FaceView.openAddContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_face_add_context', {}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                info = result.get('info', {})
            else:
                msg = result.get('msg', 'failed to get context')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("FaceView.openAddContext() res:%s" % str(res))
    return f_responseJson(res)


def api_openEditContext(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("FaceView.openEditContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_face_edit_context', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                info = result.get('info', {})
                
                if info.get('image_dir') and info.get('image_name'):
                    info['person_img_url'] = f"/storage/openAccess?filename={info['image_dir']}/{info['image_name']}&node_code={node_code}"
                if info.get('image_dir') and info.get('face_image_name'):
                    info['face_img_url'] = f"/storage/openAccess?filename={info['image_dir']}/{info['face_image_name']}&node_code={node_code}"
            else:
                msg = result.get('msg', 'failed to get context')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("FaceView.openEditContext() res:%s" % str(res))
    return f_responseJson(res)


def api_openAdd(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("FaceView.openAdd() params:%s" % str({k: v for k, v in params.items() if k != 'file_content'}))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        flow_code = params.get('flow_code', '').strip()
        group_name = params.get('group_name', '').strip()
        name = params.get('name', '').strip()
        extend_params = params.get('extend_params', '').strip()
        remark = params.get('remark', '').strip()
        file_content = params.get('file_content', '').strip()
        file_name = params.get('file_name', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not name:
            msg = "名称不能为空"
        elif not group_name:
            msg = "分组不能为空"
        elif not file_content:
            msg = "请上传人员照片"
        else:
            result = send_command_to_node_sync(node_code, 'add_face', {
                'code': code,
                'flow_code': flow_code,
                'group_name': group_name,
                'name': name,
                'extend_params': extend_params,
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
    g_logger.info("FaceView.openAdd() res:%s" % str(res))
    return f_responseJson(res)


def api_openEdit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("FaceView.openEdit() params:%s" % str({k: v for k, v in params.items() if k != 'file_content'}))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        flow_code = params.get('flow_code', '').strip()
        name = params.get('name', '').strip()
        extend_params = params.get('extend_params', '').strip()
        remark = params.get('remark', '').strip()
        file_content = params.get('file_content', '').strip()
        file_name = params.get('file_name', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        elif not name:
            msg = "名称不能为空"
        elif not file_content:
            msg = "请上传人员照片"
        else:
            result = send_command_to_node_sync(node_code, 'edit_face', {
                'code': code,
                'flow_code': flow_code,
                'name': name,
                'extend_params': extend_params,
                'remark': remark,
                'file_content': file_content,
                'file_name': file_name
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', '编辑成功')
            else:
                msg = result.get('msg', '编辑失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("FaceView.openEdit() res:%s" % str(res))
    return f_responseJson(res)


def api_openDel(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("FaceView.openDel() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        handle = params.get('handle', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            if handle == 'all':
                result = send_command_to_node_sync(node_code, 'del_face', {
                    'handle': 'all'
                }, timeout=120)
            else:
                if not code:
                    msg = "code is required"
                else:
                    result = send_command_to_node_sync(node_code, 'del_face', {
                        'code': code
                    }, timeout=120)
                
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', '删除失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("FaceView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openFlows(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("FaceView.openFlows() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_face_flows', {}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
            else:
                msg = result.get('msg', 'failed to get flows')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info("FaceView.openFlows() res:%s" % str(res))
    return f_responseJson(res)


def api_openFaceDbUpdate(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("FaceView.openFaceDbUpdate() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'update_face_db', {}, timeout=300)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                info = result.get('info', {})
            else:
                msg = result.get('msg', '更新失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("FaceView.openFaceDbUpdate() res:%s" % str(res))
    return f_responseJson(res)


def api_openFaceDbInfo(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("FaceView.openFaceDbInfo() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        group_name = params.get('group_name', 'all').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_face_db_info', {
                'group_name': group_name
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                info = result.get('info', {})
            else:
                msg = result.get('msg', '获取失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("FaceView.openFaceDbInfo() res:%s" % str(res))
    return f_responseJson(res)


def api_openFaceDbRecognize(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("FaceView.openFaceDbRecognize() params:%s" % str({k: v for k, v in params.items() if k != 'file_content'}))
        
        node_code = params.get('node_code', '').strip()
        flow_code = params.get('flow_code', '').strip()
        group_name = params.get('group_name', '').strip()
        file_content = params.get('file_content', '').strip()
        file_name = params.get('file_name', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not flow_code:
            msg = "flow_code is required"
        elif not file_content:
            msg = "请上传人员照片"
        else:
            result = send_command_to_node_sync(node_code, 'recognize_face', {
                'flow_code': flow_code,
                'group_name': group_name,
                'file_content': file_content,
                'file_name': file_name
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
            else:
                msg = result.get('msg', '识别失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info("FaceView.openFaceDbRecognize() res:%s" % str(res))
    return f_responseJson(res)
