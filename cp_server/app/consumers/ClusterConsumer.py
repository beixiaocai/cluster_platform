import json
import uuid
import threading
import time
from datetime import datetime
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from framework.settings import PROJECT_SUPPORT_REBEKAH_MIN_VERSION

g_command_responses = {}
g_command_lock = threading.Lock()

def get_ws_token():
    try:
        import os
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('wsToken', 'cp_server_safe_key_2026')
    except:
        return 'cp_server_safe_key_2026'

CP_SERVER_SAFE = get_ws_token()

class ClusterConsumer(WebsocketConsumer):
    
    def connect(self):
        self.node_code = None
        self.accept()
        print(f"ClusterConsumer.connect() new connection")
    
    def disconnect(self, close_code):
        if self.node_code:
            node_manager = self.get_node_manager()
            node_manager.unregister_node(self.channel_name)
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
        if token != CP_SERVER_SAFE:
            self.send_error("authentication failed")
            self.close()
            return
        
        discover_info = data.get('discover_info', {})
        node_code = discover_info.get('code')
        
        if not node_code:
            self.send_error("node_code is required")
            self.close()
            return
        
        import re
        if not re.match(r'^[a-zA-Z0-9]+$', node_code):
            self.send_error("node_code format invalid, only letters and numbers allowed")
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
            self.send_error_msg(f"version not supported, minimum version: {PROJECT_SUPPORT_REBEKAH_MIN_VERSION}, current version: {project_version}")
            self.close()
            return
        
        client_ip = self.scope.get('client', ['unknown', 0])[0]
        if client_ip == 'unknown':
            headers = dict(self.scope.get('headers', []))
            x_forwarded_for = headers.get(b'x-forwarded-for', b'').decode()
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(',')[0].strip()
        
        ret, node_data = node_manager.register_node(
            node_code=node_code,
            channel_name=self.channel_name,
            discover_info=discover_info,
            client_ip=client_ip
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
        
        if node_code:
            node_manager = self.get_node_manager()
            ret = node_manager.update_heartbeat(node_code)
            if ret:
                self.send(json.dumps({
                    'type': 'heartbeat_response',
                    'code': 1000,
                    'timestamp': int(datetime.now().timestamp())
                }))
            else:
                self.send_error("node not found")
        else:
            self.send_error("node_code is required")
    
    def handle_command_response(self, data):
        command_id = data.get('data', {}).get('command_id')
        code = data.get('data', {}).get('code', 0)
        msg = data.get('data', {}).get('msg', '')
        result = data.get('data', {}).get('result')
        
        print(f"ClusterConsumer.handle_command_response() command_id={command_id}, code={code}")
        
        if command_id:
            with g_command_lock:
                if command_id in g_command_responses:
                    response_result = {
                        "code": code,
                        "msg": msg
                    }
                    if result:
                        for k, v in result.items():
                            response_result[k] = v
                    
                    g_command_responses[command_id] = {
                        "status": "completed",
                        "result": response_result
                    }
    
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
    
    def send_error_msg(self, msg):
        self.send(json.dumps({
            'type': 'error',
            'code': 0,
            'msg': msg
        }))
    
    def get_node_manager(self):
        from app.utils.NodeManager import g_node_manager
        return g_node_manager


def send_command_to_node(node_code, action, params=None, timeout=30):
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


def send_command_to_node_sync(node_code, action, params=None, timeout=30):
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from app.utils.NodeManager import g_node_manager
    
    channel_layer = get_channel_layer()
    channel_name = g_node_manager.get_channel_name(node_code)
    
    if not channel_name:
        return {"code": 0, "msg": "node not connected"}
    
    command_id = str(uuid.uuid4())
    
    with g_command_lock:
        g_command_responses[command_id] = {"status": "pending", "result": None}
    
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
        return {"code": 0, "msg": f"send command error: {e}"}
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        with g_command_lock:
            if command_id in g_command_responses and g_command_responses[command_id]["status"] == "completed":
                result = g_command_responses[command_id]["result"]
                del g_command_responses[command_id]
                return result
        time.sleep(0.1)
    
    print(f"send_command_to_node_sync() timeout command_id={command_id}")
    with g_command_lock:
        if command_id in g_command_responses:
            del g_command_responses[command_id]
    
    return {"code": 0, "msg": "command timeout"}
