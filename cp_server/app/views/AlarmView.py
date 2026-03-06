from app.views.ViewsBase import *
from django.shortcuts import render
from app.utils.Utils import buildPageLabels
from app.consumers.ClusterConsumer import send_command_to_node_sync

def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    now_date = datetime.now()
    context["startDate"] = (now_date - timedelta(days=6)).strftime("%Y-%m-%d")
    context["endDate"] = now_date.strftime("%Y-%m-%d")
    return render(request, 'app/alarm/index.html', context)

def api_openIndex(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    __check_ret, __check_msg = f_checkRequestSafe(request)
    if __check_ret:
        params = f_parseGetParams(request)
        node_code = params.get('node_code', '')
        
        if not node_code:
            res = {"code": 0, "msg": "请选择节点", "data": [], "pageData": {}}
            return f_responseJson(res)
        
        page = params.get('p', 1)
        page_size = params.get('ps', 10)
        state = params.get('state', '-1')
        controlCode = params.get('controlCode', '-1')
        streamCode = params.get('streamCode', '-1')
        flowCode = params.get('flowCode', '-1')
        dateRange = params.get('dateRange', '')
        
        result = send_command_to_node_sync(node_code, 'get_alarms', {
            'p': page,
            'ps': page_size,
            'state': state,
            'controlCode': controlCode,
            'streamCode': streamCode,
            'flowCode': flowCode,
            'dateRange': dateRange
        })
        
        if result.get('code') == 1000:
            data = result.get('data', [])
            pageData = result.get('pageData', {})
            ret = True
            msg = "success"
        else:
            msg = result.get('msg', '查询失败')
    else:
        msg = __check_msg
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData
    }
    return f_responseJson(res)

def api_openInfo(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            node_code = params.get('node_code', '')
            alarm_code = params.get('code', '')
            
            if not node_code:
                res = {"code": 0, "msg": "请选择节点", "info": {}}
                return f_responseJson(res)
            
            result = send_command_to_node_sync(node_code, 'get_alarm_info', {
                'code': alarm_code
            })
            
            if result.get('code') == 1000:
                info = result.get('info', {})
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', '查询失败')
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    return f_responseJson(res)

def api_openEdit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            node_code = params.get('node_code', '')
            alarm_code = params.get('code', '')
            state = params.get('state', 1)
            review_remark = params.get('review_remark', '')
            
            if not node_code:
                res = {"code": 0, "msg": "请选择节点"}
                return f_responseJson(res)
            
            result = send_command_to_node_sync(node_code, 'edit_alarm', {
                'code': alarm_code,
                'state': state,
                'review_remark': review_remark
            })
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
            else:
                msg = result.get('msg', '操作失败')
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)

def api_openHandle(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            node_code = params.get('node_code', '')
            handle = params.get('handle', '')
            alarm_ids_str = params.get('alarm_ids_str', '')
            
            if not node_code:
                res = {"code": 0, "msg": "请选择节点"}
                return f_responseJson(res)
            
            result = send_command_to_node_sync(node_code, 'handle_alarm', {
                'handle': handle,
                'alarm_ids_str': alarm_ids_str
            })
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', '操作失败')
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)

def api_openExport(request):
    ret = False
    msg = "未知错误"
    info = {}
    
    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            node_code = params.get('node_code', '')
            alarm_ids_str = params.get('alarm_ids_str', '')
            export_format = params.get('export_format', '')
            
            if not node_code:
                res = {"code": 0, "msg": "请选择节点", "info": {}}
                return f_responseJson(res)
            
            result = send_command_to_node_sync(node_code, 'export_alarm', {
                'alarm_ids_str': alarm_ids_str,
                'export_format': export_format
            })
            
            if result.get('code') == 1000:
                info = result.get('info', {})
                ret = True
                msg = result.get('msg', 'success')
            else:
                msg = result.get('msg', '导出失败')
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    return f_responseJson(res)

def api_openContext(request):
    ret = False
    msg = "未知错误"
    context = {}
    
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            node_code = params.get('node_code', '')
            
            if not node_code:
                res = {"code": 0, "msg": "请选择节点", "context": {}}
                return f_responseJson(res)
            
            controls_result = send_command_to_node_sync(node_code, 'get_controls', {'p': 1, 'ps': 100})
            streams_result = send_command_to_node_sync(node_code, 'get_streams', {})
            
            controls = []
            streams = []
            flows = []
            
            if controls_result.get('code') == 1000:
                controls = controls_result.get('data', [])
            
            if streams_result.get('code') == 1000:
                streams = streams_result.get('data', [])
                flow_codes = set()
                for s in streams:
                    flow_code = s.get('flow_code', '')
                    if flow_code:
                        flow_codes.add(flow_code)
                for fc in flow_codes:
                    flows.append({'code': fc, 'name': fc})
            
            context = {
                'controls': controls,
                'streams': streams,
                'flows': flows
            }
            
            ret = True
            msg = "success"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "context": context
    }
    return f_responseJson(res)
