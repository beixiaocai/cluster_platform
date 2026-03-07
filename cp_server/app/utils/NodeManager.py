import threading
import time
import json
from datetime import datetime

class NodeManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._nodes = {}
        self._channels = {}
        self._lock = threading.Lock()
        self._heartbeat_timeout = 60
    
    def register_node(self, node_code, channel_name, discover_info, client_ip=None):
        with self._lock:
            auth_info = discover_info.get('auth', {})
            
            node_data = {
                'code': node_code,
                'name': discover_info.get('name', ''),
                'describe': discover_info.get('describe', ''),
                'system_name': discover_info.get('system_name', ''),
                'machine_node': discover_info.get('machine_node', ''),
                'host': discover_info.get('host', ''),
                'admin_port': discover_info.get('adminPort', 9001),
                'version': discover_info.get('project_version', 0),
                'flag': discover_info.get('project_flag', ''),
                'is_auth': 1 if auth_info.get('state', 0) == 1 else 0,
                'is_multi_process': 1 if auth_info.get('isMultiProcess', False) else 0,
                'max_count': auth_info.get('maxCount', 0),
                'auth_msg': auth_info.get('authMsg', ''),
                'finger': auth_info.get('finger', ''),
                'project_start_timestamp': discover_info.get('project_start_timestamp', 0),
                'os_boot_timestamp': discover_info.get('os_boot_timestamp', 0),
                'channel_name': channel_name,
                'connected': True,
                'connect_time': datetime.now(),
                'last_heartbeat': datetime.now(),
                'client_ip': client_ip,
                'register_info': json.dumps(discover_info, ensure_ascii=False),
            }
            
            self._nodes[node_code] = node_data
            self._channels[channel_name] = node_code
            
            self._save_node_to_db(node_data)
            
            return True, node_data
    
    def unregister_node(self, channel_name):
        with self._lock:
            node_code = self._channels.get(channel_name)
            if node_code:
                if node_code in self._nodes:
                    self._nodes[node_code]['connected'] = False
                    self._nodes[node_code]['channel_name'] = None
                    self._update_node_disconnect_db(node_code)
                del self._channels[channel_name]
                if node_code in self._nodes:
                    del self._nodes[node_code]
                return node_code
            return None
    
    def update_heartbeat(self, node_code):
        with self._lock:
            if node_code in self._nodes:
                self._nodes[node_code]['last_heartbeat'] = datetime.now()
                return True
            return False
    
    def is_node_online(self, node_code):
        with self._lock:
            return node_code in self._nodes and self._nodes[node_code].get('connected', False)
    
    def get_node(self, node_code):
        with self._lock:
            return self._nodes.get(node_code)
    
    def get_node_by_channel(self, channel_name):
        with self._lock:
            node_code = self._channels.get(channel_name)
            if node_code:
                return self._nodes.get(node_code)
            return None
    
    def get_all_nodes(self):
        with self._lock:
            return list(self._nodes.values())
    
    def get_connected_nodes(self):
        with self._lock:
            return [node for node in self._nodes.values() if node.get('connected')]
    
    def is_node_online(self, node_code):
        with self._lock:
            node = self._nodes.get(node_code)
            return node.get('connected', False) if node else False
    
    def get_channel_name(self, node_code):
        with self._lock:
            node = self._nodes.get(node_code)
            return node.get('channel_name') if node else None
    
    def check_heartbeat_timeout(self):
        now = datetime.now()
        timeout_nodes = []
        with self._lock:
            for node_code, node in list(self._nodes.items()):
                last_heartbeat = node.get('last_heartbeat')
                if last_heartbeat:
                    elapsed = (now - last_heartbeat).total_seconds()
                    if elapsed > self._heartbeat_timeout:
                        timeout_nodes.append(node_code)
        return timeout_nodes
    
    def _save_node_to_db(self, node_data):
        try:
            from app.models import NodeModel
            node, created = NodeModel.objects.update_or_create(
                code=node_data['code'],
                defaults={
                    'name': node_data.get('name', ''),
                    'describe': node_data.get('describe', ''),
                    'system_name': node_data.get('system_name', ''),
                    'machine_node': node_data.get('machine_node', ''),
                    'host': node_data.get('host', ''),
                    'admin_port': node_data.get('admin_port', 9001),
                    'version': node_data.get('version', 0),
                    'flag': node_data.get('flag', ''),
                    'is_auth': node_data.get('is_auth', 0),
                    'is_multi_process': node_data.get('is_multi_process', 0),
                    'max_count': node_data.get('max_count', 0),
                    'auth_msg': node_data.get('auth_msg', ''),
                    'finger': node_data.get('finger', ''),
                    'project_start_timestamp': node_data.get('project_start_timestamp', 0),
                    'os_boot_timestamp': node_data.get('os_boot_timestamp', 0),
                    'ws_connected': True,
                    'ws_channel': node_data.get('channel_name', ''),
                    'ws_connect_time': node_data.get('connect_time'),
                    'ws_last_heartbeat': node_data.get('last_heartbeat'),
                    'client_ip': node_data.get('client_ip', ''),
                    'register_info': node_data.get('register_info', ''),
                }
            )
            return node
        except Exception as e:
            print(f"NodeManager._save_node_to_db() error: {e}")
            return None
    
    def _update_node_disconnect_db(self, node_code):
        try:
            from app.models import NodeModel
            NodeModel.objects.filter(code=node_code).update(
                ws_connected=False,
                ws_channel='',
                ws_last_heartbeat=datetime.now()
            )
        except Exception as e:
            print(f"NodeManager._update_node_disconnect_db() error: {e}")

g_node_manager = NodeManager()
