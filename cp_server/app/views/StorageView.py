from app.views.ViewsBase import *
import os
import mimetypes

def download(request):
    params = f_parseGetParams(request)
    filename = params.get("filename", "").strip()

    if not filename:
        return f_responseJson({"code": 0, "msg": "filename is required"})

    try:
        filepath = os.path.join(g_config.storageTempDir, filename)

        if not os.path.exists(filepath):
            return f_responseJson({"code": 0, "msg": "file not found"})

        if not os.path.abspath(filepath).startswith(os.path.abspath(g_config.storageTempDir)):
            return f_responseJson({"code": 0, "msg": "access denied"})

        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        with open(filepath, 'rb') as f:
            file_content = f.read()

        response = HttpResponse(file_content, content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(file_content)

        return response
    except Exception as e:
        return f_responseJson({"code": 0, "msg": str(e)})

def access(request):
    params = f_parseGetParams(request)
    filename = params.get("filename")

    if filename:
        filename = filename.replace("//", "/")

    try:
        if filename:
            if (filename.endswith(".mp4") or
                    filename.endswith(".avi") or
                    filename.endswith(".wav") or
                    filename.endswith(".jpeg") or
                    filename.endswith(".jpg") or
                    filename.endswith(".png")):

                filepath = os.path.join(g_config.storageDir, filename)

                if os.path.exists(filepath):
                    f = open(filepath, mode="rb")
                    data = f.read()
                    f.close()

                    if filename.endswith(".mp4"):
                        fs = os.path.getsize(filepath)
                        response = HttpResponse(data, content_type="video/mp4")
                        response['Accept-Ranges'] = "bytes"
                        response['Access-Control-Allow-Origin'] = "*"
                        response['Access-Control-Allow-Headers'] = "*"
                        response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, DELETE"
                        response['Content-Length'] = fs
                    elif filename.endswith(".jpg") or filename.endswith(".png"):
                        response = HttpResponse(data, content_type="image/jpeg")
                        response['Access-Control-Allow-Origin'] = "*"
                        response['Access-Control-Allow-Headers'] = "*"
                        response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, DELETE"
                    else:
                        response = HttpResponse(data, content_type="application/octet-stream")
                        response['Access-Control-Allow-Origin'] = "*"
                        response['Access-Control-Allow-Headers'] = "*"
                        response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, DELETE"

                    return response
                else:
                    return f_responseJson({"msg": "File not found: " + filepath})
            else:
                return f_responseJson({"msg": "Unsupported format"})
        else:
            return f_responseJson({"msg": "Filename required"})

    except Exception as e:
        return f_responseJson({"msg": str(e)})

def info(request):
    return f_responseJson({"code": 0, "msg": "not implemented"})

def openAccess(request):
    params = f_parseGetParams(request)
    filename = params.get("filename", "").strip()
    node_code = params.get("node_code", "")

    if not filename:
        return f_responseJson({"code": 0, "msg": "filename is required"})

    if not node_code:
        from app.utils.NodeManager import g_node_manager
        connected_nodes = g_node_manager.get_connected_nodes()
        if connected_nodes:
            node_code = connected_nodes[0].get('code')

    if not node_code:
        return f_responseJson({"code": 0, "msg": "node_code is required"})

    result = send_command_to_node_sync(node_code, 'get_file', {
        'filename': filename
    })

    if result.get('code') != 1000:
        return f_responseJson({"code": 0, "msg": result.get('msg', 'Failed to get file')})

    data = result.get('data', {})
    base64_content = data.get('content', '')
    mime_type = data.get('mime_type', 'application/octet-stream')

    if not base64_content:
        return f_responseJson({"code": 0, "msg": "Empty file content"})

    try:
        file_content = base64.b64decode(base64_content)

        django_response = HttpResponse(
            file_content,
            content_type=mime_type
        )
        django_response['Access-Control-Allow-Origin'] = "*"
        django_response['Access-Control-Allow-Headers'] = "*"
        django_response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, DELETE"
        django_response['Content-Length'] = len(file_content)

        return django_response
    except Exception as e:
        return f_responseJson({"code": 0, "msg": str(e)})
