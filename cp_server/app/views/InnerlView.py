from app.views.ViewsBase import *
from app.models import *
import threading

"""
内部服务调用的接口
"""

def api_on_stream_not_found(request):
    ret = False
    msg = "unknown error"
    key = ""

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.debug("on_stream_not_found() params:%s" % str(params))

        _app = params.get("app", "").strip()
        _stream = params.get("stream", "").strip()
        _schema = params.get("schema", "").strip()
        _vhost = params.get("vhost", "").strip()

        node_code = _app
        _stream_array = _stream.split("-")
        
        if len(_stream_array) >= 2:
            stream_app = _stream_array[0]
            stream_name = "-".join(_stream_array[1:])
            dst_stream_app = _app
            dst_stream_name = _stream
            
            pusher_params = {
                'stream_app': stream_app,
                'stream_name': stream_name,
                'dst_stream_app': dst_stream_app,
                'dst_stream_name': dst_stream_name,
                'dst_host': g_config.externalHost,
                'dst_rtsp_port': g_config.mediaRtspPort,
                'dst_http_port': g_config.mediaHttpPort,
                'dst_secret': g_config.mediaSecret
            }
            
            result = send_command_to_node_sync(node_code, 'add_stream_pusher', pusher_params, timeout=120)
            
            g_logger.debug("on_stream_not_found() add_stream_pusher result:%s" % str(result))
            
            if result.get('code') == 1000:
                ret = True
                msg = "success"
                data = result.get('data') or {}
                key = result.get('key', '') or data.get('key', '')
            else:
                msg = result.get('msg', 'failed to start pusher')
        else:
            msg = "unsupported stream app=%s,stream=%s" % (_app, _stream)
    else:
        msg = "request method not supported"

    res = {
        "code": 0,
        "msg": "success"
    }
    g_logger.debug("on_stream_not_found() ret=%d,msg=%s,key=%s" % (ret, msg, str(key)))
    return f_responseJson(res)
