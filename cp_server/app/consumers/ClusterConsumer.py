import json
import os
import re
import uuid
import threading
import time
from datetime import datetime
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from framework.settings import PROJECT_SUPPORT_REBEKAH_MIN_VERSION

g_command_responses = {}
g_command_lock = threading.RLock()  # 使用RLock支持递归锁定
g_command_events = {}
MAX_COMMAND_ENTRIES = 1000  # 最大命令条目数，防止内存泄漏

def _cleanup_old_commands():
    """清理旧的命令条目，防止内存无限增长"""
    global g_command_responses, g_command_events
    with g_command_lock:
        if len(g_command_responses) > MAX_COMMAND_ENTRIES:
            entries_to_remove = int(MAX_COMMAND_ENTRIES * 0.2)
            old_keys = list(g_command_responses.keys())[:entries_to_remove]
            for key in old_keys:
                del g_command_responses[key]
                if key in g_command_events:
                    del g_command_events[key]
            print(f"ClusterConsumer._cleanup_old_commands() cleaned up {entries_to_remove} old entries")

def get_ws_token():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('wsToken', 'cp_server_safe_key_2026')
    except:
        return 'cp_server_safe_key_2026'

CP_WS_TOKEN = get_ws_token()

class ClusterConsumer(WebsocketConsumer):
    
    def connect(self):
        self.node_code = None
        self.accept()
        print(f"ClusterConsumer.connect() new connection")
    
    def disconnect(self, close_code):
        node_manager = self.get_node_manager()
        node_manager.unregister_node(self.channel_name)
        if self.node_code:
            print(f"ClusterConsumer.disconnect() node_code={self.node_code}")
    
    def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'register':
                self.handle_register(data)
            elif message_type == 'heartbeat':
                self.handle_heartbeat(data)
            elif message_type == 'command_response':
                self.handle_command_response(data)
            elif message_type == 'alarm_report':
                self.handle_alarm_report(data)
            else:
                self.send_error(f"unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            self.send_error("invalid json format")
        except Exception as e:
            print(f"ClusterConsumer.receive() error: {e}")
            self.send_error(str(e))
    
    def handle_register(self, data):
        token = data.get('token')
        if token != CP_WS_TOKEN:
            self.send_error("authentication failed")
            self.close()
            return
        
        discover_info = data.get('discover_info', {})
        node_code = discover_info.get('code')
        
        if not node_code:
            self.send_error("node_code is required")
            self.close()
            return
        
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', node_code):
            self.send_error("node_code format invalid, only letters, numbers, underscore, hyphen and dot allowed")
            self.close()
            return
        
        if len(node_code) > 64:
            self.send_error("node_code too long, maximum 64 characters")
            self.close()
            return
        
        node_manager = self.get_node_manager()
        if node_manager.is_node_online(node_code):
            self.send_error(f"node_code '{node_code}' already connected")
            self.close()
            return
        
        project_version = discover_info.get('project_version', 0)
        try:
            version_float = float(project_version)
        except (ValueError, TypeError):
            version_float = 0
        
        if version_float < PROJECT_SUPPORT_REBEKAH_MIN_VERSION:
            self.send_error(f"version not supported, minimum version: {PROJECT_SUPPORT_REBEKAH_MIN_VERSION}, current version: {project_version}")
            self.close()
            return
        
        client_ip = self.scope.get('client', ['unknown', 0])[0]
        if client_ip == 'unknown':
            headers = dict(self.scope.get('headers', []))
            x_forwarded_for = headers.get(b'x-forwarded-for', b'').decode()
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(',')[0].strip()
            else:
                x_real_ip = headers.get(b'x-real-ip', b'').decode()
                if x_real_ip:
                    client_ip = x_real_ip
        
        if client_ip == 'unknown':
            client_ip = None
        
        ret, node_data = node_manager.register_node(
            node_code=node_code,
            channel_name=self.channel_name,
            discover_info=discover_info,
            client_ip=client_ip,
            consumer=self
        )
        
        if ret:
            self.node_code = node_code
            self.send(json.dumps({
                'type': 'register_response',
                'code': 1000,
                'msg': 'success',
                'data': {
                    'node_id': node_data.get('id') if node_data else None,
                    'node_code': node_code
                }
            }))
            print(f"ClusterConsumer.handle_register() success node_code={node_code}, client_ip={client_ip}")
        else:
            self.send_error("register failed")
    
    def handle_heartbeat(self, data):
        node_code = data.get('data', {}).get('node_code')
        
        if not node_code:
            node_code = self.node_code
        
        # 验证心跳的node_code与当前连接的node_code匹配
        if node_code and self.node_code and node_code != self.node_code:
            print(f"ClusterConsumer.handle_heartbeat() node_code mismatch, expected={self.node_code}, got={node_code}")
            self.send(json.dumps({
                'type': 'heartbeat_response',
                'code': 0,
                'msg': 'node_code mismatch',
                'need_register': True
            }))
            return
        
        if node_code:
            node_manager = self.get_node_manager()
            client_ip = self.scope.get('client', ['unknown', 0])[0]
            if client_ip == 'unknown':
                client_ip = None
            
            ret = node_manager.update_heartbeat(node_code, client_ip)
            if ret:
                self.send(json.dumps({
                    'type': 'heartbeat_response',
                    'code': 1000,
                    'timestamp': int(datetime.now().timestamp())
                }))
            else:
                self.send(json.dumps({
                    'type': 'heartbeat_response',
                    'code': 0,
                    'msg': 'node not found, please re-register',
                    'need_register': True
                }))
        else:
            self.send_error("node_code is required")
    
    def handle_command_response(self, data):
        command_id = data.get('data', {}).get('command_id')
        code = data.get('data', {}).get('code', 0)
        msg = data.get('data', {}).get('msg', '')
        result = data.get('data', {}).get('result')
        
        print(f"ClusterConsumer.handle_command_response() command_id={command_id}, code={code}, node_code={self.node_code}")
        
        if command_id:
            with g_command_lock:
                if command_id in g_command_responses:
                    command_info = g_command_responses[command_id]
                    if command_info.get('node_code') != self.node_code:
                        print(f"ClusterConsumer.handle_command_response() node_code mismatch, expected={command_info.get('node_code')}, got={self.node_code}")
                        return
                    
                    response_result = {
                        "code": code,
                        "msg": msg
                    }
                    if result:
                        for k, v in result.items():
                            response_result[k] = v
                    
                    g_command_responses[command_id]["result"] = response_result
                    
                    if command_id in g_command_events:
                        g_command_events[command_id].set()
    
    def handle_alarm_report(self, data):
        alarm_data = data.get('data', {})
        print(f"ClusterConsumer.handle_alarm_report() node_code={self.node_code}")
    
    def send_command(self, event):
        command_id = event.get('command_id')
        action = event.get('action')
        params = event.get('params', {})
        
        print(f"ClusterConsumer.send_command() action={action}, command_id={command_id}")
        
        self.send(json.dumps({
            'type': 'command',
            'data': {
                'command_id': command_id,
                'action': action,
                'params': params
            }
        }))
    
    def send_error(self, msg):
        self.send(json.dumps({
            'type': 'error',
            'code': 0,
            'msg': msg
        }))
    
    def get_node_manager(self):
        from app.utils.NodeManager import g_node_manager
        return g_node_manager


def send_command_to_node(node_code, action, params=None, timeout=120):
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from app.utils.NodeManager import g_node_manager
    
    channel_layer = get_channel_layer()
    channel_name = g_node_manager.get_channel_name(node_code)
    
    if not channel_name:
        return False, "node not connected"
    
    command_id = str(uuid.uuid4())
    
    async_to_sync(channel_layer.send)(channel_name, {
        'type': 'send.command',
        'command_id': command_id,
        'action': action,
        'params': params or {}
    })
    
    return True, command_id


def send_command_to_node_sync(node_code, action, params=None, timeout=120):
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from app.utils.NodeManager import g_node_manager
    
    channel_layer = get_channel_layer()
    channel_name = g_node_manager.get_channel_name(node_code)
    
    if not channel_name:
        return {"code": 0, "msg": "node not connected"}
    
    command_id = str(uuid.uuid4())
    event = threading.Event()
    
    with g_command_lock:
        # 先清理旧条目，再检查是否超过限制
        _cleanup_old_commands()
        
        # 如果清理后仍然超过限制，拒绝新命令
        if len(g_command_responses) >= MAX_COMMAND_ENTRIES:
            print(f"send_command_to_node_sync() command queue full, rejecting command for node={node_code}")
            return {"code": 0, "msg": "command queue full, try again later"}
        
        g_command_responses[command_id] = {
            "status": "pending",
            "result": None,
            "node_code": node_code
        }
        g_command_events[command_id] = event
    
    try:
        async_to_sync(channel_layer.send)(channel_name, {
            'type': 'send.command',
            'command_id': command_id,
            'action': action,
            'params': params or {}
        })
        print(f"send_command_to_node_sync() sent command_id={command_id}, action={action}")
    except Exception as e:
        print(f"send_command_to_node_sync() send error: {e}")
        with g_command_lock:
            if command_id in g_command_responses:
                del g_command_responses[command_id]
            if command_id in g_command_events:
                del g_command_events[command_id]
        return {"code": 0, "msg": f"send command error: {e}"}
    
    if event.wait(timeout):
        with g_command_lock:
            if command_id in g_command_responses:
                result = g_command_responses[command_id].get("result")
                del g_command_responses[command_id]
            else:
                result = {"code": 0, "msg": "response already cleaned up"}
            if command_id in g_command_events:
                del g_command_events[command_id]
        return result
    
    print(f"send_command_to_node_sync() timeout command_id={command_id}")
    with g_command_lock:
        if command_id in g_command_responses:
            del g_command_responses[command_id]
        if command_id in g_command_events:
            del g_command_events[command_id]
    
    return {"code": 0, "msg": "command timeout"}