from django.db import models

class NodeModel(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='节点编号')
    name = models.CharField(max_length=100, verbose_name='节点名称')
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name='昵称')
    describe = models.TextField(blank=True, null=True, verbose_name='描述')
    
    system_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='系统名称')
    machine_node = models.CharField(max_length=100, blank=True, null=True, verbose_name='机器节点名')
    finger = models.CharField(max_length=100, blank=True, null=True, verbose_name='机器指纹')
    host = models.CharField(max_length=100, blank=True, null=True, verbose_name='内网主机地址')
    admin_port = models.IntegerField(default=9001, verbose_name='管理端口')
    
    version = models.FloatField(default=0, verbose_name='版本号')
    flag = models.CharField(max_length=50, blank=True, null=True, verbose_name='项目标识')
    
    is_auth = models.IntegerField(default=0, verbose_name='是否授权')
    is_multi_process = models.IntegerField(default=0, verbose_name='是否多进程')
    max_count = models.IntegerField(default=0, verbose_name='最大布控数')
    auth_msg = models.CharField(max_length=200, blank=True, null=True, verbose_name='授权消息')
    
    ws_connected = models.BooleanField(default=False, verbose_name='WebSocket连接状态')
    ws_channel = models.CharField(max_length=200, blank=True, null=True, verbose_name='WebSocket通道')
    ws_connect_time = models.DateTimeField(blank=True, null=True, verbose_name='连接时间')
    
    client_ip = models.CharField(max_length=50, blank=True, null=True, verbose_name='客户端IP')
    register_info = models.TextField(blank=True, null=True, verbose_name='注册信息')
    
    project_start_timestamp = models.IntegerField(default=0, verbose_name='软件启动时间戳')
    os_boot_timestamp = models.IntegerField(default=0, verbose_name='系统启动时间戳')
    
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


class NodeHeartModel(models.Model):
    node_code = models.CharField(max_length=50, verbose_name='节点编号')
    heartbeat_time = models.DateTimeField(verbose_name='心跳时间')
    client_ip = models.CharField(max_length=50, blank=True, null=True, verbose_name='客户端IP')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    def __repr__(self):
        return f"{self.node_code} - {self.heartbeat_time}"

    def __str__(self):
        return f"{self.node_code} - {self.heartbeat_time}"

    class Meta:
        db_table = 'cp_node_heart'
        verbose_name = 'cp_node_heart'
        verbose_name_plural = 'cp_node_heart'
        ordering = ['-heartbeat_time']
        indexes = [
            models.Index(fields=['node_code']),
            models.Index(fields=['heartbeat_time']),
        ]


class PlatformAlarmModel(models.Model):
    sort = models.IntegerField(verbose_name='sort')
    code = models.CharField(max_length=50, verbose_name='code')
    draw_type = models.IntegerField(verbose_name='合成报警视频画框类型')
    flag = models.CharField(max_length=50, verbose_name='合成报警视频标记')
    node_code = models.CharField(max_length=100, verbose_name='node_code')
    control_code = models.CharField(max_length=50, verbose_name='布控编号')
    desc = models.CharField(max_length=200, verbose_name='描述')
    video_path = models.TextField(verbose_name='视频存储路径')
    video_count = models.IntegerField(verbose_name='视频总数量')
    image_path = models.TextField(verbose_name='主图存储路径')
    image_count = models.IntegerField(verbose_name='图片总数量')
    other_image_count = models.IntegerField(verbose_name='其他图片数量')
    level = models.IntegerField(verbose_name='报警级别')
    state = models.IntegerField(verbose_name='状态')
    is_check = models.IntegerField(verbose_name='是否检测')
    review_remark = models.CharField(max_length=200, verbose_name='审核备注')
    stream_app = models.CharField(max_length=50, verbose_name='视频流应用')
    stream_name = models.CharField(max_length=100, verbose_name='视频流名称')
    stream_code = models.CharField(max_length=50, verbose_name='视频流编号')
    flow_mode = models.IntegerField(verbose_name='业务算法模式')
    flow_code = models.CharField(max_length=50, verbose_name='业务算法编号')
    flow_name = models.CharField(max_length=100, verbose_name='业务算法名称')
    main_plate_color = models.IntegerField(verbose_name='关键帧车牌颜色', default=0)
    main_plate_type = models.IntegerField(verbose_name='关键帧车牌类型', default=0)
    main_plate_no = models.CharField(max_length=100, verbose_name='关键帧车牌号', default='')
    main_track_max_code = models.CharField(max_length=50, verbose_name='特征最大匹配编号', default='')
    main_track_max_custom_code = models.CharField(max_length=50, verbose_name='特征最大匹配自定义编号', default='')
    main_track_max_similary = models.IntegerField(verbose_name='特征最大相似度', default=0)
    expand1 = models.CharField(max_length=200, verbose_name='expand1', default='')
    expand2 = models.CharField(max_length=200, verbose_name='expand2', default='')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    create_timestamp = models.IntegerField(verbose_name='create_timestamp')
    last_update_time = models.DateTimeField(verbose_name='last_update_time')

    def __repr__(self):
        return self.desc

    def __str__(self):
        return self.desc

    def delete(self, using=None, keep_parents=False):
        ret = super(PlatformAlarmModel, self).delete(using, keep_parents)
        return ret

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        ret = super(PlatformAlarmModel, self).save(force_insert, force_update, using, update_fields)
        return ret

    class Meta:
        db_table = 'cp_platform_alarm'
        verbose_name = 'cp_platform_alarm'
        verbose_name_plural = 'cp_platform_alarm'


class PlatformStreamModel(models.Model):
    sort = models.IntegerField(verbose_name='排序')
    stream_code = models.CharField(max_length=50, verbose_name='stream_code')
    stream_nickname = models.CharField(max_length=100, verbose_name='stream_nickname')
    node_codes = models.TextField(verbose_name='节点编号列表')
    state = models.IntegerField(verbose_name='状态')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    last_update_time = models.DateTimeField(verbose_name='last_update_time')

    def __repr__(self):
        return self.stream_code

    def __str__(self):
        return self.stream_code

    class Meta:
        db_table = 'cp_platform_stream'
        verbose_name = 'cp_platform_stream'
        verbose_name_plural = 'cp_platform_stream'


class PlatformAlgorithmFlowModel(models.Model):
    sort = models.IntegerField(verbose_name='排序')
    flow_code = models.CharField(max_length=50, verbose_name='flow_code')
    flow_name = models.CharField(max_length=100, verbose_name='flow_name')
    node_codes = models.TextField(verbose_name='节点编号列表')
    state = models.IntegerField(verbose_name='状态')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    last_update_time = models.DateTimeField(verbose_name='last_update_time')

    def __repr__(self):
        return self.flow_code

    def __str__(self):
        return self.flow_code

    class Meta:
        db_table = 'cp_platform_algorithm_flow'
        verbose_name = 'cp_platform_algorithm_flow'
        verbose_name_plural = 'cp_platform_algorithm_flow'
