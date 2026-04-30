# 常见问题 (FAQ)

[功能特性](#功能特性) • [节点连接](#节点连接) • [视频与录像](#视频与录像) • [配置与部署](#配置与部署)

---

## 节点连接

### Q: 节点注册后显示离线？

**A:** 检查以下几点：
1. 确认节点端 `config.json` 中的 `cpServerUrl` 地址正确，格式为 `ws://cp_server_ip:9824/ws/cluster`
2. 确认 `wsToken` 与 cp_server 的 `config.json` 中一致
3. 确认节点版本 ≥ `PROJECT_SUPPORT_REBEKAH_MIN_VERSION`（当前要求 1.009+），版本过低会被拒绝连接
4. 检查防火墙是否放行 9824 端口
5. 查看节点端日志是否有 `authentication failed` 或 `version not supported` 提示

### Q: 节点频繁掉线？

**A:** 默认心跳超时为 60 秒，检查：
1. 网络是否稳定，特别是公网-内网之间的链路
2. 节点端是否正常运行，未出现进程崩溃
3. 如果网络延迟较高，可适当增大 `NodeManager` 中的 `_heartbeat_timeout` 值

### Q: 同一个 node_code 能否同时连接多个 cp_server？

**A:** 不能。同一个 node_code 只能连接一个 cp_server 实例，重复注册会被拒绝并断开连接。

### Q: 节点重连后命令执行失败？

**A:** 节点断线重连后需要重新注册，注册成功后才能接收命令。如果重连后仍失败，检查节点端 `ClusterClient` 是否正常启动。

---

## 视频与录像

### Q: 录像播放很慢？

**A:** 录像文件通过 WebSocket 从内网节点传输到公网 cp_server，再返回给浏览器，链路为：
```
浏览器 → cp_server → WebSocket → 节点读取文件 → base64编码 → WebSocket回传 → base64解码 → 浏览器
```
60MB 的 MP4 文件 base64 编码后约 80MB，传输耗时较长。这是公网-内网架构的固有限制，建议在需要频繁查看录像时直接访问内网节点的管理界面。

### Q: 录像时间轴显示空白？

**A:** 检查：
1. 该流是否开启了录像计划（`is_record = 1`）
2. 选择的时间范围内是否确实有录像文件
3. 节点端录像目录是否存在且权限正常

### Q: 点击录像切片无法播放？

**A:** 检查：
1. 节点是否在线，离线节点无法获取录像文件
2. 浏览器控制台是否有跨域错误
3. 录像文件是否已被清理（超过保留天数）

---

## 配置与部署

### Q: 支持哪些数据库？

**A:** 支持 MySQL 和 SQLite。生产环境推荐 MySQL，SQLite 仅适用于测试。在 `framework/settings.py` 中切换。

### Q: cp_server 必须部署在公网吗？

**A:** 不必须，但推荐。cp_server 部署在公网可以让内网节点主动连接，无需开放内网端口。如果所有节点和 cp_server 在同一内网，也可以内网部署。

### Q: 如何修改默认登录密码？

**A:** 登录后在"用户管理"中修改。默认账号 `admin`，密码 `admin888`。

### Q: 如何配置 ZLMediaKit 流媒体？

**A:** 在 `config.json` 中配置 `zlm` 相关参数：
- `zlmHttpPort`：ZLMediaKit HTTP API 端口（默认 80）
- `zlmSecret`：ZLMediaKit API 密钥
- `zlmRtmpPort`：RTMP 端口（默认 1935）
- `zlmRtspPort`：RTSP 端口（默认 554）
- `zlmHttpFlvPort`：HTTP-FLV 端口（默认 8080）

确保 cp_zlm 进程已启动。

### Q: 如何更换数据库从 SQLite 到 MySQL？

**A:**
1. 创建 MySQL 数据库并导入 `cluster_platform.sql`
2. 修改 `framework/settings.py` 中的 `DATABASES` 配置
3. 安装 `mysqlclient`：`pip install mysqlclient`
4. 重启 cp_server

### Q: 端口 9824 被占用怎么办？

**A:** 修改启动命令中的端口号：
```bash
python manage.py runserver 0.0.0.0:你的端口
```
同时需要修改节点端 `config.json` 中的 `cpServerUrl` 端口。

### Q: 如何查看日志？

**A:** 日志文件位于 `cp_server/log/` 目录下，文件名格式为 `cp_server_日期-时间.log`。

---

## 安全相关

### Q: wsToken 的作用是什么？

**A:** `wsToken` 是节点连接 cp_server 的认证令牌，必须与 cp_server 的 `config.json` 中一致，否则连接会被拒绝。

### Q: Safe 请求头是什么？

**A:** API 请求的安全校验字段，值必须与 `config.json` 中的 `safe` 一致。用于非浏览器端的 API 调用认证。

---

## 版本与兼容

### Q: 节点版本要求？

**A:** 节点（rebekah）版本必须 ≥ `PROJECT_SUPPORT_REBEKAH_MIN_VERSION`，否则注册会被拒绝。当前最低要求版本见 `framework/settings.py`。

### Q: 如何升级 cp_server？

**A:**
1. 备份数据库和 `config.json`
2. 拉取最新代码
3. 执行 `pip install -r requirements.txt` 更新依赖
4. 如有 SQL 变更，手动执行增量 SQL
5. 重启服务
