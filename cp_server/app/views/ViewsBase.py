import os
import shutil
import time
import platform
import requests
from datetime import datetime, timedelta
import json
import base64
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import random
from django.http import HttpResponse
from django.shortcuts import render
from framework.settings import BASE_DIR, PROJECT_UA, PROJECT_BUILT, PROJECT_VERSION, PROJECT_FLAG, PROJECT_ADMIN_START_TIMESTAMP
from app.utils.ZLMediaKit import ZLMediaKit
from app.utils.Config import Config
from app.utils.Logger import CreateLogger
from app.utils.OSSystem import OSSystem
from app.utils.Database import Database

from app.models import *
from app.consumers.ClusterConsumer import send_command_to_node_sync

g_filepath_config_json = os.path.join(BASE_DIR, "config.json")

# 从 config.json 读取所有配置（包括 OEM 配置）
g_config = Config(filepath=g_filepath_config_json)

# OEM 配置从 config.json 的 oem 子字典读取
class OemConfig:
    """OEM 配置类，从 config.json 的 oem 字段读取"""
    def __init__(self):
        try:
            with open(g_filepath_config_json, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                self.data = config_data.get('oem', {})
        except Exception as e:
            g_logger.error("OemConfig.__init__() error: %s" % str(e)) if 'g_logger' in globals() else print("OemConfig error:", e)
            self.data = {}
        
        # 解析具体字段
        self.name = self.data.get("name", "集群管理平台")
        self.welcome = self.data.get("welcome", "欢迎")
        self.logo_url = self.data.get("logo_url", "/static/images/logo.png")
        self.bottom_name = self.data.get("bottom_name", "集群管理平台")
        self.is_show_author = bool(self.data.get("is_show_author", True))
        self.author = self.data.get("author", "宇图瑞视")
        self.author_link = self.data.get("author_link", "https://www.yuturuishi.com/")
        self.auth_online_link = self.data.get("auth_online_link", "https://www.yuturuishi.com")
        self.enable_update = bool(self.data.get("enable_update", True))
        self.check_version_download_url = self.data.get("check_version_download_url", "https://github.com/beixiaocai/cluster_platform")
    
    def getStr(self):
        return str(self.data)

g_settings = OemConfig()

__log_dir = os.path.join(BASE_DIR, "log")
if not os.path.exists(__log_dir):
    os.makedirs(__log_dir)
g_logger = CreateLogger(filepath=os.path.join(__log_dir, "cp_server%s.log" % (datetime.now().strftime("%Y%m%d-%H%M%S"))),
                        is_show_console=False,
                        log_debug=g_config.logDebug)

g_logger.info("%s v%s,%s" % (PROJECT_UA, PROJECT_VERSION, PROJECT_FLAG))
g_logger.info(PROJECT_BUILT)
g_logger.info("g_filepath_config_json=%s" % g_filepath_config_json)
g_logger.info("config.json:%s" % g_config.getStr())
g_logger.info("oem config data loaded from config.json")
g_logger.info("logDebug=%d" % g_config.logDebug)
g_osSystem = OSSystem()
g_zlm = ZLMediaKit(logger=g_logger, config=g_config)
g_database = Database(logger=g_logger)

g_session_key_user = "user"
g_session_key_captcha = "captcha"

def get_node_manager():
    from app.utils.NodeManager import g_node_manager
    return g_node_manager

def f_parseGetParams(request):
    params = {}
    try:
        for k in request.GET:
            params.__setitem__(k, request.GET.get(k))
    except Exception as e:
        params = {}
    return params

def f_parsePostParams(request):
    params = {}
    for k in request.POST:
        params.__setitem__(k, request.POST.get(k))
    if not params:
        try:
            params = request.body.decode('utf-8')
            params = json.loads(params)
        except:
            params = {}
    return params

def f_parseRequestIp(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    except Exception as e:
        g_logger.error("f_parseRequestIp() error: %s" % str(e))
        ip = "0.0.0.0"
    return ip

def f_parseRequestPort(request):
    return 0

def f_sessionReadUser(request):
    user = request.session.get(g_session_key_user)
    return user

def f_sessionReadUserId(request):
    try:
        user_id = f_sessionReadUser(request).get("id")
    except:
        user_id = 0
    return user_id

def f_checkRequestSafe(request):
    ret = False
    msg = "未知错误"
    user_id = f_sessionReadUserId(request)
    if user_id:
        ret = True
        msg = "success"
    else:
        headers = request.headers
        Safe = headers.get("Safe")
        if Safe and Safe == g_config.safe:
            ret = True
            msg = "success"
        else:
            msg = "safe verify error"
    return ret, msg

def f_sessionLogout(request):
    if request.session.has_key(g_session_key_user):
        del request.session[g_session_key_user]
    if request.session.has_key(g_session_key_captcha):
        del request.session[g_session_key_captcha]

def f_responseJson(res):
    def json_dumps_default(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError
    return HttpResponse(json.dumps(res, default=json_dumps_default), content_type="application/json")

def f_checkNode(node_code):
    ret = False
    msg = "未知错误"
    node = None
    if not node_code:
        msg = "node_code is required"
    else:
        try:
            node = NodeModel.objects.get(code=node_code)
            ret = True
            msg = "success"
        except NodeModel.DoesNotExist:
            msg = "node not found: %s" % node_code
    return ret, msg, node
