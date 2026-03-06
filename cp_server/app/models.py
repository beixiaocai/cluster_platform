from django.db import models

class NodeModel(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='节点编号')
    name = models.CharField(max_length=100, verbose_name='节点名称')
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name='昵称')
    describe = models.TextField(blank=True, null=True, verbose_name='描述')
    
    system_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='系统名称')
    machine_node = models.CharField(max_length=100, blank=True, null=True, verbose_name='机器节点名')
    machine_mac = models.CharField(max_length=50, blank=True, null=True, verbose_name='MAC地址')
    host = models.CharField(max_length=100, blank=True, null=True, verbose_name='内网主机地址')
    admin_port = models.IntegerField(default=9001, verbose_name='管理端口')
    
    version = models.FloatField(default=0, verbose_name='版本号')
    flag = models.CharField(max_length=50, blank=True, null=True, verbose_name='项目标识')
    
    is_auth = models.IntegerField(default=0, verbose_name='是否授权')
    is_multi_process = models.IntegerField(default=0, verbose_name='是否多进程')
    max_count = models.IntegerField(default=0, verbose_name='最大布控数')
    auth_desc = models.CharField(max_length=200, blank=True, null=True, verbose_name='授权描述')
    
    ws_connected = models.BooleanField(default=False, verbose_name='WebSocket连接状态')
    ws_channel = models.CharField(max_length=200, blank=True, null=True, verbose_name='WebSocket通道')
    ws_connect_time = models.DateTimeField(blank=True, null=True, verbose_name='连接时间')
    ws_last_heartbeat = models.DateTimeField(blank=True, null=True, verbose_name='最后心跳时间')
    
    client_ip = models.CharField(max_length=50, blank=True, null=True, verbose_name='客户端IP')
    register_info = models.TextField(blank=True, null=True, verbose_name='注册信息')
    
    start_timestamp = models.IntegerField(default=0, verbose_name='启动时间戳')
    
    expand1 = models.CharField(max_length=200, blank=True, null=True, verbose_name='扩展字段1')
    expand2 = models.CharField(max_length=200, blank=True, null=True, verbose_name='扩展字段2')
    
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'cp_node'
        verbose_name = 'cp_node'
        verbose_name_plural = 'cp_node'
