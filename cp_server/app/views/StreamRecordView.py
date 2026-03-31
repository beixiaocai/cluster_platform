from django.shortcuts import render
from app.views.ViewsBase import *


def index(request):
    context = {
        "settings": g_settings.data
    }
    nodes = NodeModel.objects.all().order_by('-id')
    context["nodes"] = nodes
    return render(request, 'app/streamRecord/index.html', context)


def timeplayer(request):
    context = {
        "settings": g_settings.data
    }
    params = f_parseGetParams(request)
    record_code = params.get("code", "").strip()
    node_code = params.get("node_code", "").strip()
    
    context["record_code"] = record_code
    context["node_code"] = node_code
    
    record_day = 7
    if record_code and node_code:
        try:
            result = send_command_to_node_sync(node_code, 'get_stream_record_info', {'code': record_code}, timeout=120)
            if result.get('code') == 1000:
                info = result.get('info', {})
                record_day = info.get('record_day', 7)
        except Exception as e:
            g_logger.error(f"StreamRecordView.timeplayer() error: {str(e)}")
    
    context["record_day"] = record_day
    
    return render(request, 'app/streamRecord/timeplayer.html', context)


def api_getList(request):
    ret = False
    msg = "未知错误"
    data = []

    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("StreamRecordView.api_getList() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        page = int(params.get('p', 1))
        page_size = int(params.get('ps', 10))

        if not node_code:
            msg = "node_code is required"
        else:
            try:
                result = send_command_to_node_sync(node_code, 'get_stream_records', {}, timeout=120)

                if result.get('code') == 1000:
                    ret = True
                    msg = "success"
                    all_data = result.get('data', [])
                    total_count = len(all_data)
                    skip = (page - 1) * page_size
                    data = all_data[skip:skip + page_size]
                else:
                    msg = result.get('msg', 'failed to get stream records')
            except Exception as e:
                msg = f"获取录像计划失败：{str(e)}"
                g_logger.error(f"StreamRecordView.api_getList() error: {str(e)}")
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "page": page if 'page' in dir() else 1,
        "page_size": page_size if 'page_size' in dir() else 10,
        "total_count": total_count if 'total_count' in dir() else 0
    }
    g_logger.info(f"StreamRecordView.api_getList() res: {str(res)}")
    return f_responseJson(res)


def api_getInfo(request):
    ret = False
    msg = "未知错误"
    info = {}

    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("StreamRecordView.api_getInfo() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        record_code = params.get('code', '').strip()

        if not node_code:
            msg = "node_code is required"
        elif not record_code:
            msg = "code is required"
        else:
            try:
                result = send_command_to_node_sync(node_code, 'get_stream_record_info', {'code': record_code}, timeout=120)

                if result.get('code') == 1000:
                    ret = True
                    msg = "success"
                    info = result.get('info', {})
                else:
                    msg = result.get('msg', 'failed to get stream record info')
            except Exception as e:
                msg = f"获取录像计划详情失败：{str(e)}"
                g_logger.error(f"StreamRecordView.api_getInfo() error: {str(e)}")
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info(f"StreamRecordView.api_getInfo() res: {str(res)}")
    return f_responseJson(res)


def api_getStreams(request):
    ret = False
    msg = "未知错误"
    data = []

    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("StreamRecordView.api_getStreams() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()

        if not node_code:
            msg = "node_code is required"
        else:
            try:
                result = send_command_to_node_sync(node_code, 'get_streams', {}, timeout=120)

                if result.get('code') == 1000:
                    ret = True
                    msg = "success"
                    data = result.get('data', [])
                else:
                    msg = result.get('msg', 'failed to get streams')
            except Exception as e:
                msg = f"获取视频流列表失败：{str(e)}"
                g_logger.error(f"StreamRecordView.api_getStreams() error: {str(e)}")
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info(f"StreamRecordView.api_getStreams() res: {str(res)}")
    return f_responseJson(res)


def api_add(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamRecordView.api_add() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        stream_code = params.get('stream_code', '').strip()
        audio_type = int(params.get('audio_type', 0))
        is_record = int(params.get('is_record', 0))
        record_day = int(params.get('record_day', 7))

        if not node_code:
            msg = "node_code is required"
        elif not stream_code:
            msg = "stream_code is required"
        else:
            try:
                result = send_command_to_node_sync(node_code, 'add_stream_record', {
                    'stream_code': stream_code,
                    'audio_type': audio_type,
                    'is_record': is_record,
                    'record_day': record_day
                }, timeout=120)

                if result.get('code') == 1000:
                    ret = True
                    msg = "添加成功"
                else:
                    msg = result.get('msg', 'failed to add stream record')
            except Exception as e:
                msg = f"添加录像计划失败：{str(e)}"
                g_logger.error(f"StreamRecordView.api_add() error: {str(e)}")
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info(f"StreamRecordView.api_add() res: {str(res)}")
    return f_responseJson(res)


def api_edit(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamRecordView.api_edit() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        record_code = params.get('code', '').strip()
        audio_type = int(params.get('audio_type', 0))
        is_record = int(params.get('is_record', 0))
        record_day = int(params.get('record_day', 7))

        if not node_code:
            msg = "node_code is required"
        elif not record_code:
            msg = "code is required"
        else:
            try:
                result = send_command_to_node_sync(node_code, 'edit_stream_record', {
                    'code': record_code,
                    'audio_type': audio_type,
                    'is_record': is_record,
                    'record_day': record_day
                }, timeout=120)

                if result.get('code') == 1000:
                    ret = True
                    msg = "编辑成功"
                else:
                    msg = result.get('msg', 'failed to edit stream record')
            except Exception as e:
                msg = f"编辑录像计划失败：{str(e)}"
                g_logger.error(f"StreamRecordView.api_edit() error: {str(e)}")
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info(f"StreamRecordView.api_edit() res: {str(res)}")
    return f_responseJson(res)


def api_del(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("StreamRecordView.api_del() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        record_code = params.get('code', '').strip()

        if not node_code:
            msg = "node_code is required"
        elif not record_code:
            msg = "code is required"
        else:
            try:
                result = send_command_to_node_sync(node_code, 'del_stream_record', {
                    'code': record_code
                }, timeout=120)

                if result.get('code') == 1000:
                    ret = True
                    msg = "删除成功"
                else:
                    msg = result.get('msg', 'failed to delete stream record')
            except Exception as e:
                msg = f"删除录像计划失败：{str(e)}"
                g_logger.error(f"StreamRecordView.api_del() error: {str(e)}")
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info(f"StreamRecordView.api_del() res: {str(res)}")
    return f_responseJson(res)


def api_getRecordTimeline(request):
    ret = False
    msg = "未知错误"
    data = []

    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("StreamRecordView.api_getRecordTimeline() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        record_code = params.get('code', '').strip()
        timestamp = int(params.get('timestamp', 0))

        if not node_code:
            msg = "node_code is required"
        elif not record_code:
            msg = "code is required"
        else:
            try:
                result = send_command_to_node_sync(node_code, 'get_record_timeline', {
                    'code': record_code,
                    'timestamp': timestamp
                }, timeout=120)

                if result.get('code') == 1000:
                    ret = True
                    msg = "success"
                    data = result.get('data', [])
                else:
                    msg = result.get('msg', 'failed to get record timeline')
            except Exception as e:
                msg = f"获取录像时间线失败：{str(e)}"
                g_logger.error(f"StreamRecordView.api_getRecordTimeline() error: {str(e)}")
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data
    }
    g_logger.info(f"StreamRecordView.api_getRecordTimeline() res: {str(res)}")
    return f_responseJson(res)


def api_getRecordFilename(request):
    ret = False
    msg = "未知错误"
    info = {}

    if request.method == 'GET':
        params = f_parseGetParams(request)
        g_logger.info("StreamRecordView.api_getRecordFilename() params:%s" % str(params))

        node_code = params.get('node_code', '').strip()
        record_code = params.get('code', '').strip()
        timestamp = int(params.get('timestamp', 0))

        if not node_code:
            msg = "node_code is required"
        elif not record_code:
            msg = "code is required"
        else:
            try:
                result = send_command_to_node_sync(node_code, 'get_record_filename', {
                    'code': record_code,
                    'timestamp': timestamp
                }, timeout=120)

                if result.get('code') == 1000:
                    ret = True
                    msg = "success"
                    info = result.get('info', {})
                    
                    if info.get('filename'):
                        filename = info.get('filename')
                        info['filename'] = "/storage/openAccess?filename=%s&node_code=%s" % (filename, node_code)
                else:
                    msg = result.get('msg', 'failed to get record filename')
            except Exception as e:
                msg = f"获取录像文件失败：{str(e)}"
                g_logger.error(f"StreamRecordView.api_getRecordFilename() error: {str(e)}")
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info(f"StreamRecordView.api_getRecordFilename() res: {str(res)}")
    return f_responseJson(res)
