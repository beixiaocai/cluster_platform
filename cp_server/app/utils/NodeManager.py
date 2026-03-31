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
        self._consumers = {}
        self._lock = threading.Lock()
        self._heartbeat_timeout = 60
        self._checker_interval = 30
        self._checker_thread = None
        self._checker_running = False
        self._heartbeat_buffer = {}  # 心跳缓冲，用于批量写入
        self._heartbeat_buffer_lock = threading.Lock()
    
    def register_node(self, node_code, channel_name, discover_info, client_ip=None, consumer=None):
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
            if consumer:
                self._consumers[channel_name] = consumer
            
            self._save_node_to_db(node_data)
            
            return True, node_data
    
    def unregister_node(self, channel_name):
        with self._lock:
            node_code = self._channels.get(channel_name)
            if node_code:
                # 更新节点状态为断开
                if node_code in self._nodes:
                    self._nodes[node_code]['connected'] = False
                    self._nodes[node_code]['channel_name'] = None
                    self._update_node_disconnect_db(node_code)
                    del self._nodes[node_code]
                
                # 清理通道和消费者映射
                del self._channels[channel_name]
                if channel_name in self._consumers:
                    del self._consumers[channel_name]
            return None
    
    def update_heartbeat(self, node_code, client_ip=None):
        with self._lock:
            if node_code in self._nodes:
                now = datetime.now()
                self._nodes[node_code]['last_heartbeat'] = now
                # 使用缓冲，减少数据库写入频率
                with self._heartbeat_buffer_lock:
                    self._heartbeat_buffer[node_code] = {
                        'heartbeat_time': now,
                        'client_ip': client_ip
                    }
                return True
            return False
    
    def flush_heartbeat_buffer(self):
        """批量刷新心跳数据到数据库"""
        with self._heartbeat_buffer_lock:
            buffer_copy = self._heartbeat_buffer.copy()
            self._heartbeat_buffer.clear()
        
        if not buffer_copy:
            return
        
        try:
            from app.models import NodeHeartModel
            
            # 批量创建心跳记录
            heartbeats_to_create = []
            nodes_to_cleanup = []
            
            for node_code, data in buffer_copy.items():
                heartbeats_to_create.append(NodeHeartModel(
                    node_code=node_code,
                    heartbeat_time=data['heartbeat_time'],
                    client_ip=data['client_ip']
                ))
                nodes_to_cleanup.append(node_code)
            
            if heartbeats_to_create:
                NodeHeartModel.objects.bulk_create(heartbeats_to_create)
                print(f"NodeManager.flush_heartbeat_buffer() flushed {len(heartbeats_to_create)} heartbeats")
                
                # 批量清理旧记录（只清理超过 100 条的节点）
                self._batch_cleanup_old_heartbeats(nodes_to_cleanup, keep_count=100)
        except Exception as e:
            print(f"NodeManager.flush_heartbeat_buffer() error: {e}")
            # 失败时将数据放回缓冲区（但不覆盖已有的新数据）
            with self._heartbeat_buffer_lock:
                for node_code, data in buffer_copy.items():
                    if node_code not in self._heartbeat_buffer:
                        self._heartbeat_buffer[node_code] = data
                    else:
                        # 比较时间，只保留较新的心跳
                        existing_time = self._heartbeat_buffer[node_code]['heartbeat_time']
                        if data['heartbeat_time'] > existing_time:
                            self._heartbeat_buffer[node_code] = data
    
    def _batch_cleanup_old_heartbeats(self, node_codes, keep_count=100):
        """批量清理多个节点的旧心跳记录"""
        try:
            from app.models import NodeHeartModel
            
            ids_to_delete = []
            for node_code in node_codes:
                # 检查是否需要清理
                total_count = NodeHeartModel.objects.filter(node_code=node_code).count()
                if total_count > keep_count:
                    # 获取要删除的 ID（保留最新的 keep_count 条）
                    old_heartbeats = NodeHeartModel.objects.filter(
                        node_code=node_code
                    ).order_by('-heartbeat_time')[keep_count:].values_list('id', flat=True)
                    ids_to_delete.extend(old_heartbeats)
            
            # 批量删除
            if ids_to_delete:
                NodeHeartModel.objects.filter(id__in=ids_to_delete).delete()
                print(f"NodeManager._batch_cleanup_old_heartbeats() deleted {len(ids_to_delete)} old heartbeats")
        except Exception as e:
            print(f"NodeManager._batch_cleanup_old_heartbeats() error: {e}")
    
    def _save_heartbeat_to_db(self, node_code, heartbeat_time, client_ip=None):
        """单个心跳写入（兼容旧代码）"""
        try:
            from app.models import NodeHeartModel
            NodeHeartModel.objects.create(
                node_code=node_code,
                heartbeat_time=heartbeat_time,
                client_ip=client_ip
            )
            self._cleanup_old_heartbeats(node_code)
        except Exception as e:
            print(f"NodeManager._save_heartbeat_to_db() error: {e}")
    
    def _cleanup_old_heartbeats(self, node_code, keep_count=100):
        try:
            from app.models import NodeHeartModel
            old_heartbeats = NodeHeartModel.objects.filter(
                node_code=node_code
            ).order_by('-heartbeat_time')[keep_count:]
            if old_heartbeats:
                old_ids = [h.id for h in old_heartbeats]
                NodeHeartModel.objects.filter(id__in=old_ids).delete()
        except Exception as e:
            print(f"NodeManager._cleanup_old_heartbeats() error: {e}")
    
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
    
    def unregister_node_by_code(self, node_code, close_connection=True):
        consumer_to_close = None
        channel_name = None
        node_found = False
        
        with self._lock:
            if node_code in self._nodes:
                node_found = True
                node = self._nodes[node_code]
                channel_name = node.get('channel_name')
                
                if close_connection and channel_name and channel_name in self._consumers:
                    consumer_to_close = self._consumers[channel_name]
                
                if channel_name and channel_name in self._channels:
                    del self._channels[channel_name]
                if channel_name and channel_name in self._consumers:
                    del self._consumers[channel_name]
                self._update_node_disconnect_db(node_code)
                del self._nodes[node_code]
        
        if consumer_to_close:
            try:
                consumer_to_close.close()
                print(f"NodeManager.unregister_node_by_code() closed websocket for node_code={node_code}")
            except Exception as e:
                print(f"NodeManager.unregister_node_by_code() close connection error: {e}")
        
        if node_found:
            print(f"NodeManager.unregister_node_by_code() node_code={node_code}")
        return node_found
    
    def start_heartbeat_checker(self):
        if self._checker_running:
            return
        self._checker_running = True
        self._checker_thread = threading.Thread(target=self._heartbeat_checker_loop, daemon=True)
        self._checker_thread.start()
        print("NodeManager.start_heartbeat_checker() heartbeat checker started")
    
    def stop_heartbeat_checker(self):
        self._checker_running = False
        if self._checker_thread:
            self._checker_thread.join(timeout=5)
            self._checker_thread = None
        print("NodeManager.stop_heartbeat_checker() heartbeat checker stopped")
    
    def _heartbeat_checker_loop(self):
        while self._checker_running:
            try:
                # 批量刷新心跳缓冲区到数据库（失败时保留缓冲区数据，下次重试）
                try:
                    self.flush_heartbeat_buffer()
                except Exception as e:
                    print(f"NodeManager._heartbeat_checker_loop() flush heartbeat buffer error: {e}")
                    # 不清除缓冲区，下次重试
                
                # 检查超时节点
                timeout_nodes = self.check_heartbeat_timeout()
                for node_code in timeout_nodes:
                    print(f"NodeManager._heartbeat_checker_loop() node {node_code} heartbeat timeout")
                    self.unregister_node_by_code(node_code)
            except Exception as e:
                print(f"NodeManager._heartbeat_checker_loop() error: {e}")
            time.sleep(self._checker_interval)
    
    def reset_all_nodes_offline(self):
        try:
            from app.models import NodeModel
            NodeModel.objects.update(ws_connected=False, ws_channel='')
            print("NodeManager.reset_all_nodes_offline() all nodes set to offline")
        except Exception as e:
            print(f"NodeManager.reset_all_nodes_offline() error: {e}")
    
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
                ws_channel=''
            )
        except Exception as e:
            print(f"NodeManager._update_node_disconnect_db() error: {e}")

g_node_manager = NodeManager()
