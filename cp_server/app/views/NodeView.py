import os
import time
from datetime import datetime

from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels, gen_random_code_s

def index(request):
    context = {
        "settings": f_settingsReadData()
    }

    data = []
    params = f_parseGetParams(request)

    page = params.get('p', 1)
    page_size = params.get('ps', 10)
    search_keyword = params.get('keyword', '').strip()
    
    try:
        page = int(page)
    except:
        page = 1

    try:
        page_size = int(page_size)
        if page_size < 1:
            page_size = 1
    except:
        page_size = 10

    skip = (page - 1) * page_size
    
    if search_keyword:
        from django.db.models import Q
        nodes_query = NodeModel.objects.filter(
            Q(code__icontains=search_keyword) | Q(name__icontains=search_keyword) | Q(finger__icontains=search_keyword)
        ).order_by('-id')
        count = nodes_query.count()
        nodes = nodes_query[skip:skip+page_size]
    else:
        nodes = NodeModel.objects.all().order_by('-id')[skip:skip+page_size]
        count = NodeModel.objects.count()

    data = []
    for node in nodes:
        node_dict = {
            'id': node.id,
            'code': node.code,
            'name': node.name,
            'nickname': node.nickname,
            'describe': node.describe,
            'system_name': node.system_name,
            'machine_node': node.machine_node,
            'host': node.host,
            'admin_port': node.admin_port,
            'version': node.version,
            'flag': node.flag,
            'is_auth': node.is_auth,
            'is_multi_process': node.is_multi_process,
            'max_count': node.max_count,
            'auth_msg': node.auth_msg,
            'finger': node.finger,
            'ws_connected': node.ws_connected,
            'ws_channel': node.ws_channel,
            'ws_connect_time': node.ws_connect_time,
            'client_ip': node.client_ip,
            'register_info': node.register_info,
            'project_start_timestamp': node.project_start_timestamp,
            'os_boot_timestamp': node.os_boot_timestamp,
            'create_time': node.create_time,
            'last_update_time': node.last_update_time,
        }
        
        online_node = get_node_manager().get_node(node.code)
        if online_node:
            node_dict['online'] = True
            node_dict['online_last_heartbeat'] = online_node.get('last_heartbeat')
        else:
            node_dict['online'] = False
        
        data.append(node_dict)

    page_num = int(count / page_size)
    if count % page_size > 0:
        page_num += 1
    pageLabels = buildPageLabels(page=page, page_num=page_num)
    pageData = {
        "page": page,
        "page_size": page_size,
        "page_num": page_num,
        "count": count,
        "pageLabels": pageLabels
    }

    context["data"] = data
    context["pageData"] = pageData
    context["keyword"] = search_keyword
    return render(request, 'app/node/index.html', context)


def edit(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        handle = request.POST.get("handle", "")
        code = request.POST.get("code", "").strip()
        nickname = request.POST.get("nickname", "").strip()
        describe = request.POST.get("describe", "").strip()
        
        params = {
            "handle": handle,
            "code": code,
            "nickname": nickname,
            "describe": describe
        }
        g_logger.info("NodeView.edit() params:%s" % str(params))

        try:
            if handle != "edit":
                raise Exception("request parameters are incorrect")

            node = NodeModel.objects.filter(code=code).first()
            if node:
                node.nickname = nickname
                node.describe = describe
                node.last_update_time = datetime.now()
                node.save()

                __msg = "编辑成功"
                __ret = True
            else:
                __msg = "该节点不存在"
        except Exception as e:
            __msg = str(e)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            res = {
                "code": 1000 if __ret else 0,
                "msg": __msg
            }
            g_logger.info("NodeView.edit() ajax res:%s" % str(res))
            return f_responseJson(res)
        else:
            if __ret:
                redirect_url = "/node/index"
            else:
                redirect_url = "/node/edit?code=" + code
            g_logger.info("NodeView.edit() ret=%d,msg=%s" % (__ret, __msg))
            return render(request, 'app/message.html',
                          {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})

    else:
        context = {
            "settings": f_settingsReadData()
        }
        params = f_parseGetParams(request)
        code = params.get("code")
        if code:
            node = NodeModel.objects.filter(code=code).first()
            if node:
                context["handle"] = "edit"
                context["node"] = node
                return render(request, 'app/node/edit.html', context)
            else:
                return render(request, 'app/message.html',
                              {"msg": "该节点不存在", "is_success": False, "redirect_url": "/node/index"})
        else:
            return redirect("/node/index")


def api_openDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        code = request.POST.get("code")
        g_logger.info("NodeView.openDel() code:%s" % code)

        if code:
            get_node_manager().unregister_node_by_code(code)
            
            from app.models import NodeHeartModel
            NodeHeartModel.objects.filter(node_code=code).delete()
            
            node = NodeModel.objects.filter(code=code).first()
            if node:
                if node.delete():
                    ret = True
                    msg = "success"
                else:
                    msg = "failed to delete model"
            else:
                ret = True
                msg = "success"
        else:
            msg = "code is required"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("NodeView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openNodeDetail(request):
    ret = False
    msg = "未知错误"
    data = {}
    if request.method == 'GET':
        code = request.GET.get('code', '')
        g_logger.info("NodeView.openNodeDetail() code:%s" % code)
        
        if code:
            node = NodeModel.objects.filter(code=code).first()
            if node:
                data = {
                    'id': node.id,
                    'code': node.code,
                    'name': node.name,
                    'nickname': node.nickname,
                    'describe': node.describe,
                    'system_name': node.system_name,
                    'machine_node': node.machine_node,
                    'host': node.host,
                    'version': node.version,
                    'flag': node.flag,
                    'is_auth': node.is_auth,
                    'is_multi_process': node.is_multi_process,
                    'max_count': node.max_count,
                    'ws_connected': node.ws_connected,
                    'ws_connect_time': node.ws_connect_time,
                }
                ret = True
                msg = "success"
            else:
                msg = "the data does not exist"
        else:
            msg = "code is required"
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info("NodeView.openNodeDetail() res:%s" % str(res))
    return f_responseJson(res)


def api_getOnlineNodes(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'GET':
        try:
            online_nodes = get_node_manager().get_connected_nodes()
            for node in online_nodes:
                data.append({
                    'code': node.get('code'),
                    'name': node.get('name'),
                    'host': node.get('host'),
                    'last_heartbeat': node.get('last_heartbeat').isoformat() if node.get('last_heartbeat') else None,
                })
            ret = True
            msg = "success"
        except Exception as e:
            msg = str(e)
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_upgradeVersion(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                upload_file = request.FILES.get('file')
                if not upload_file:
                    msg = "请选择升级包文件"
                else:
                    if not upload_file.name.endswith('.xcupdate'):
                        msg = "升级包必须是.xcupdate格式"
                    else:
                        file_content = upload_file.read()
                        file_base64 = base64.b64encode(file_content).decode('utf-8')
                        
                        result = send_command_to_node_sync(node_code, 'upgrade_version', {
                            'filename': upload_file.name,
                            'content': file_base64
                        }, timeout=600)
                        
                        if result.get('code') == 1000:
                            ret = True
                            msg = result.get('msg', '升级成功')
                        else:
                            msg = result.get('msg', '升级失败')
        except Exception as e:
            msg = f"升级失败：{str(e)}"
            g_logger.error(f"NodeView.api_upgradeVersion() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info(f"NodeView.api_upgradeVersion() res: {str(res)}")
    return f_responseJson(res)


def api_restartApp(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'restart_app', {}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '重启软件指令已发送')
                else:
                    msg = result.get('msg', '重启软件失败')
        except Exception as e:
            msg = f"重启软件失败：{str(e)}"
            g_logger.error(f"NodeView.api_restartApp() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info(f"NodeView.api_restartApp() res: {str(res)}")
    return f_responseJson(res)


def api_restartOS(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            if not node_code:
                msg = "node_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'restart_os', {}, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '重启系统指令已发送')
                else:
                    msg = result.get('msg', '重启系统失败')
        except Exception as e:
            msg = f"重启系统失败：{str(e)}"
            g_logger.error(f"NodeView.api_restartOS() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info(f"NodeView.api_restartOS() res: {str(res)}")
    return f_responseJson(res)


def api_getList(request):
    ret = False
    msg = "未知错误"
    data = []
    
    if request.method == 'GET':
        try:
            nodes = NodeModel.objects.all().order_by('-id')
            for node in nodes:
                data.append({
                    'id': node.id,
                    'code': node.code,
                    'name': node.name,
                    'nickname': node.nickname,
                })
            ret = True
            msg = "success"
        except Exception as e:
            msg = str(e)
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    return f_responseJson(res)


def api_exportLogs(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'POST':
        try:
            node_code = request.POST.get('node_code', '').strip()
            is_export_stream = int(request.POST.get('is_export_stream', 0))
            
            if not node_code:
                msg = "node_code is required"
            else:
                result = send_command_to_node_sync(node_code, 'export_logs', {
                    'isExportStream': is_export_stream
                }, timeout=120)
                
                if result.get('code') == 1000:
                    ret = True
                    msg = result.get('msg', '导出成功')
                    info = result.get('info', {})
                else:
                    msg = result.get('msg', '导出失败')
        except Exception as e:
            msg = f"导出失败：{str(e)}"
            g_logger.error(f"NodeView.api_exportLogs() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info(f"NodeView.api_exportLogs() res: {str(res)}")
    return f_responseJson(res)


def api_downloadLog(request):
    """通过WebSocket下载节点上的日志文件"""
    try:
        node_code = request.GET.get('node_code', '').strip()
        filename = request.GET.get('filename', '').strip()
        
        if not node_code or not filename:
            return f_responseJson({'code': 0, 'msg': 'Missing parameters'})
        
        result = send_command_to_node_sync(node_code, 'download_file', {
            'filename': filename
        }, timeout=300)
        
        if result.get('code') == 1000:
            file_content_base64 = result.get('data', {}).get('content', '')
            file_content = base64.b64decode(file_content_base64)
            
            http_response = HttpResponse(
                content=file_content,
                content_type='application/octet-stream'
            )
            http_response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return http_response
        else:
            return f_responseJson({'code': 0, 'msg': result.get('msg', 'Download failed')})
            
    except Exception as e:
        g_logger.error(f"NodeView.api_downloadLog() error: {str(e)}")
        return f_responseJson({'code': 0, 'msg': str(e)})


def api_getHeartbeats(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        try:
            from app.models import NodeHeartModel
            
            node_code = request.GET.get('node_code', '').strip()
            page = request.GET.get('p', 1)
            page_size = request.GET.get('ps', 20)
            
            try:
                page = int(page)
            except:
                page = 1
            
            try:
                page_size = int(page_size)
                if page_size < 1:
                    page_size = 20
                elif page_size > 100:
                    page_size = 100
            except:
                page_size = 20
            
            if not node_code:
                msg = "node_code is required"
            else:
                query = NodeHeartModel.objects.filter(node_code=node_code)
                count = query.count()
                
                skip = (page - 1) * page_size
                heartbeats = query[skip:skip+page_size]
                
                for hb in heartbeats:
                    data.append({
                        'id': hb.id,
                        'node_code': hb.node_code,
                        'heartbeat_time': hb.heartbeat_time.isoformat() if hb.heartbeat_time else None,
                        'client_ip': hb.client_ip,
                        'create_time': hb.create_time.isoformat() if hb.create_time else None,
                    })
                
                page_num = int(count / page_size)
                if count % page_size > 0:
                    page_num += 1
                
                pageData = {
                    "page": page,
                    "page_size": page_size,
                    "page_num": page_num,
                    "count": count,
                }
                
                ret = True
                msg = "success"
        except Exception as e:
            msg = str(e)
            g_logger.error(f"NodeView.api_getHeartbeats() error: {str(e)}")
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData
    }
    return f_responseJson(res)
