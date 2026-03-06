from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.consumers.ClusterConsumer import send_command_to_node_sync
import requests
import os
import random


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
            }, timeout=30)
            
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


def __get_node_info(node_code):
    try:
        node = NodeModel.objects.filter(code=node_code, state=1).first()
        if node:
            return {
                'code': node.code,
                'name': node.name,
                'host': node.host,
                'port': node.port,
                'safe_key': node.safe_key
            }
    except Exception as e:
        g_logger.error(f"__get_node_info error: {e}")
    return None


def api_openAdd(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        g_logger.info("AudioView.openAdd() processing file upload")
        
        node_code = request.POST.get('node_code', '').strip()
        code = request.POST.get('code', '').strip()
        name = request.POST.get('name', '').strip()
        remark = request.POST.get('remark', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not name:
            msg = "名称不能为空"
        elif not code:
            msg = "编号不能为空"
        else:
            file = request.FILES.get('file')
            if not file:
                msg = "请上传音频文件"
            else:
                try:
                    file_size = file.size
                    file_size_m = int(file_size / 1024 / 1024)
                    
                    if file_size_m > 20:
                        msg = f"音频文件不能超过20M: {file_size_m}M"
                    else:
                        node_info = __get_node_info(node_code)
                        if not node_info:
                            msg = "节点不存在或已离线"
                        else:
                            file_name_suffix = file.name.split(".")[-1]
                            temp_file_name = f"audio{random.randint(10000, 99999)}.{file_name_suffix}"
                            temp_file_path = os.path.join(g_config.storageTempDir, temp_file_name)
                            
                            with open(temp_file_path, 'wb') as f:
                                for chunk in file.chunks():
                                    f.write(chunk)
                            
                            download_url = f"http://{g_config.externalHost}:{g_config.adminPort}/storage/download?filename={temp_file_name}"
                            
                            node_url = f"http://{node_info['host']}:{node_info['port']}/audio/openAddFromCluster"
                            headers = {"Safe": node_info['safe_key']}
                            
                            form_data = {
                                'code': code,
                                'name': name,
                                'remark': remark,
                                'download_url': download_url
                            }
                            
                            response = requests.post(node_url, data=form_data, headers=headers, timeout=60)
                            
                            if response.status_code == 200:
                                result = response.json()
                                if result.get('code') == 1000:
                                    ret = True
                                    msg = "添加成功"
                                else:
                                    msg = result.get('msg', '添加失败')
                            else:
                                msg = f"节点返回错误: HTTP {response.status_code}"
                except Exception as e:
                    msg = f"处理失败: {str(e)}"
                    g_logger.error(f"AudioView.openAdd error: {e}")
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
            result = send_command_to_node_sync(node_code, 'edit_audio', params, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'del_audio', {'code': code}, timeout=30)
            
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
            result = send_command_to_node_sync(node_code, 'get_audio_info', {'code': code}, timeout=30)
            
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
