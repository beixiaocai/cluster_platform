from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect


def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    return render(request, 'app/scheduleTask/index.html', context)


def api_openIndex(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ScheduleTaskView.openIndex() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        page = params.get('p', 1)
        page_size = params.get('ps', 12)
        search_text = params.get('search_text', '').strip()
        search_state = params.get('search_state', -1)
        
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
                page_size = 12
            try:
                search_state = int(search_state)
            except:
                search_state = -1
            
            result = send_command_to_node_sync(node_code, 'get_schedule_tasks', {
                'p': page,
                'ps': page_size,
                'search_text': search_text,
                'search_state': search_state
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
                pageData = result.get('pageData', {})
            else:
                msg = result.get('msg', 'failed to get schedule tasks')
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
    context = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ScheduleTaskView.openAddContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_schedule_task_add_context', {}, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                context = result.get('context', {})
            else:
                msg = result.get('msg', 'failed to get context')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "context": context
    }
    return f_responseJson(res)


def api_openEditContext(request):
    ret = False
    msg = "未知错误"
    context = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ScheduleTaskView.openEditContext() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'get_schedule_task_edit_context', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                context = result.get('context', {})
            else:
                msg = result.get('msg', 'failed to get context')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "context": context
    }
    return f_responseJson(res)


def api_openAdd(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ScheduleTaskView.openAdd() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        name = params.get('name', '').strip()
        task_type = params.get('task_type', 'cron').strip()
        
        cron_hour = params.get('cron_hour', '*').strip()
        cron_minute = params.get('cron_minute', '0').strip()
        cron_day = params.get('cron_day', '*').strip()
        cron_month = params.get('cron_month', '*').strip()
        cron_day_of_week = params.get('cron_day_of_week', '*').strip()
        
        interval_seconds = params.get('interval_seconds', 60)
        
        start_time = params.get('start_time', '').strip()
        end_time = params.get('end_time', '').strip()
        
        http_method = params.get('http_method', 'GET').strip()
        http_url = params.get('http_url', '').strip()
        http_headers = params.get('http_headers', '').strip()
        http_params = params.get('http_params', '').strip()
        http_body = params.get('http_body', '').strip()
        
        remark = params.get('remark', '').strip()
        state = params.get('state', 1)
        
        if not node_code:
            msg = "node_code is required"
        elif not name:
            msg = "任务名称不能为空"
        elif not http_url:
            msg = "请求地址不能为空"
        else:
            result = send_command_to_node_sync(node_code, 'add_schedule_task', {
                'code': code,
                'name': name,
                'task_type': task_type,
                'cron_hour': cron_hour,
                'cron_minute': cron_minute,
                'cron_day': cron_day,
                'cron_month': cron_month,
                'cron_day_of_week': cron_day_of_week,
                'interval_seconds': interval_seconds,
                'start_time': start_time,
                'end_time': end_time,
                'http_method': http_method,
                'http_url': http_url,
                'http_headers': http_headers,
                'http_params': http_params,
                'http_body': http_body,
                'remark': remark,
                'state': state
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
    g_logger.info("ScheduleTaskView.openAdd() res:%s" % str(res))
    return f_responseJson(res)


def api_openEdit(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ScheduleTaskView.openEdit() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        name = params.get('name', '').strip()
        task_type = params.get('task_type', 'cron').strip()
        
        cron_hour = params.get('cron_hour', '*').strip()
        cron_minute = params.get('cron_minute', '0').strip()
        cron_day = params.get('cron_day', '*').strip()
        cron_month = params.get('cron_month', '*').strip()
        cron_day_of_week = params.get('cron_day_of_week', '*').strip()
        
        interval_seconds = params.get('interval_seconds', 60)
        
        start_time = params.get('start_time', '').strip()
        end_time = params.get('end_time', '').strip()
        
        http_method = params.get('http_method', 'GET').strip()
        http_url = params.get('http_url', '').strip()
        http_headers = params.get('http_headers', '').strip()
        http_params = params.get('http_params', '').strip()
        http_body = params.get('http_body', '').strip()
        
        remark = params.get('remark', '').strip()
        state = params.get('state', 1)
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        elif not name:
            msg = "任务名称不能为空"
        elif not http_url:
            msg = "请求地址不能为空"
        else:
            result = send_command_to_node_sync(node_code, 'edit_schedule_task', {
                'code': code,
                'name': name,
                'task_type': task_type,
                'cron_hour': cron_hour,
                'cron_minute': cron_minute,
                'cron_day': cron_day,
                'cron_month': cron_month,
                'cron_day_of_week': cron_day_of_week,
                'interval_seconds': interval_seconds,
                'start_time': start_time,
                'end_time': end_time,
                'http_method': http_method,
                'http_url': http_url,
                'http_headers': http_headers,
                'http_params': http_params,
                'http_body': http_body,
                'remark': remark,
                'state': state
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
    g_logger.info("ScheduleTaskView.openEdit() res:%s" % str(res))
    return f_responseJson(res)


def api_openDel(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ScheduleTaskView.openDel() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'del_schedule_task', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', '删除成功')
            else:
                msg = result.get('msg', '删除失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ScheduleTaskView.openDel() res:%s" % str(res))
    return f_responseJson(res)


def api_openToggleState(request):
    ret = False
    msg = "未知错误"
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ScheduleTaskView.openToggleState() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'toggle_schedule_task_state', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', '操作成功')
            else:
                msg = result.get('msg', '操作失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("ScheduleTaskView.openToggleState() res:%s" % str(res))
    return f_responseJson(res)


def api_openRunNow(request):
    ret = False
    msg = "未知错误"
    result_text = ""
    
    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("ScheduleTaskView.openRunNow() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        code = params.get('code', '').strip()
        
        if not node_code:
            msg = "node_code is required"
        elif not code:
            msg = "code is required"
        else:
            result = send_command_to_node_sync(node_code, 'run_schedule_task_now', {
                'code': code
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = result.get('msg', '执行成功')
                result_text = result.get('result', '')
            else:
                msg = result.get('msg', '执行失败')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "result": result_text
    }
    g_logger.info("ScheduleTaskView.openRunNow() res:%s" % str(res))
    return f_responseJson(res)


def api_openLogs(request):
    ret = False
    msg = "未知错误"
    data = []
    pageData = {}
    
    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("ScheduleTaskView.openLogs() params:%s" % str(params))
        
        node_code = params.get('node_code', '').strip()
        task_code = params.get('task_code', '').strip()
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
            
            result = send_command_to_node_sync(node_code, 'get_schedule_task_logs', {
                'task_code': task_code,
                'p': page,
                'ps': page_size
            }, timeout=120)
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data', [])
                pageData = result.get('pageData', {})
            else:
                msg = result.get('msg', 'failed to get logs')
    else:
        msg = "request method not supported"
    
    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData
    }
    return f_responseJson(res)
