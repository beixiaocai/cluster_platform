from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render


def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    return render(request, 'app/index.html', context)


def api_getIndex(request):
    ret = False
    msg = "未知错误"
    appInfo = {}
    osInfo = {}

    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            osSystem = OSSystem()
            appInfo = {
                "project_ua": PROJECT_UA,
                "project_version": PROJECT_VERSION,
                "project_flag": PROJECT_FLAG,
                "project_built": PROJECT_BUILT,
                "start_timestamp": PROJECT_ADMIN_START_TIMESTAMP
            }
            osInfo = osSystem.getOSInfo()
            ret = True
            msg = "success"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "osInfo": osInfo,
        "appInfo": appInfo
    }
    return f_responseJson(res)
