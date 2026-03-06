# Cluster Platform - 集群管理平台

<div align="center">

![Version](https://img.shields.io/badge/version-0.002-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Django](https://img.shields.io/badge/django-5.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**一个轻量级、高性能的视频分析集群管理平台**

[功能特性](#功能特性) • [快速开始](#快速开始) • [架构设计](#架构设计) • [配置说明](#配置说明) • [部署指南](#部署指南) • [常见问题](#常见问题)

</div>

---

## 项目简介

Cluster Platform（集群管理平台）是一个专为视频分析场景设计的轻量级集群管理系统，**支持 Rebekah 视频行为分析系统 v5.002+ 版本**。

### 核心价值

- 🚀 **轻量级架构**：基于 SQLite 数据库，无需额外安装 MySQL/PostgreSQL，开箱即用
- 🌐 **跨网络部署**：支持公网部署管理端，内网部署节点端，通过 WebSocket 实现内网穿透
- ⚡ **WebSocket 通信**：实时双向通信，支持心跳检测、命令下发、文件传输
- 📹 **流媒体集成**：内置 ZLMediaKit 流媒体服务器，支持多协议和按需推流
- 🔐 **安全认证**：Token 认证 + 加密传输，确保通信安全
- 📦 **高度集成**：与 Rebekah 平台无缝集成，统一管理所有节点
- 📊 **实时监控**：实时监控节点状态、流状态和系统运行情况
- 🎯 **按需推流**：智能判断推流需求，无人观看时自动停止，节省带宽
- 🔧 **远程控制**：支持远程重启、配置更新等操作
- 📱 **响应式设计**：支持 PC、平板和手机等多种设备访问

### 应用场景

- **多节点管理**：同时管理多个视频分析节点，统一监控和配置
- **跨网络监控**：公网部署管理端，内网部署节点端，无需 VPN 即可远程管理
- **按需推流**：用户查看视频时才推流，节省带宽和服务器资源
- **集中报警管理**：汇聚所有节点的报警信息，统一处理和分析
- **远程设备控制**：通过 WebSocket 远程控制设备，无需现场操作
- **大规模部署**：支持成百上千个节点的大规模集群管理

---

## 目录结构

```
cluster_platform/
├── cp_server/                 # 管理中心服务
│   ├── app/                   # 应用核心代码
│   │   ├── consumers/         # WebSocket 消费者
│   │   ├── utils/             # 工具类
│   │   ├── views/             # 视图层
│   │   └── models.py          # 数据模型
│   ├── framework/             # Django 配置
│   ├── static/                # 静态资源
│   ├── templates/             # 模板文件
│   ├── config.json            # 配置文件
│   ├── manage.py              # Django 管理脚本
│   ├── requirements.txt       # Python 依赖
│   └── requirements-linux.txt # Linux 依赖
│
├── cp_zlm/                    # 流媒体服务器
│   ├── bin.x86.windows10/     # Windows 可执行文件
│   ├── bin.x86.gcc9.4/        # Linux x86 可执行文件
│   └── bin.arm.gcc9.4/        # Linux ARM 可执行文件
│
└── README.md                  # 项目说明文档
```

---

## 功能特性

### cp_server（管理中心）

#### 核心功能

- **节点管理**：节点注册、状态监控、版本控制、心跳检测、远程重启
- **视频流管理**：视频流代理、按需推流、单屏播放、多屏预览、流状态监控
- **报警管理**：报警记录查看、报警图片预览、报警状态处理、报警统计
- **音频管理**：音频文件管理、在线播放、音频广播
- **布控管理**：布控任务配置、布控算法关联、布控状态监控
- **系统管理**：用户管理、权限控制、系统配置、日志导出
- **存储管理**：文件下载、存储访问、远程文件获取
- **日志管理**：系统日志、操作日志、节点日志、错误日志
- **统计分析**：节点在线率、报警统计、推流统计、系统性能分析

### cp_zlm（流媒体服务器）

- 基于 ZLMediaKit 的高性能流媒体服务器
- 支持 RTSP/RTMP/HTTP-FLV/WebSocket-FLV/HLS 等协议
- 支持按需推流，无人观看自动停止，节省带宽和资源
- 支持流代理功能，自动拉取远程流，实现跨网络视频传输
- 支持 API 控制，与 cp_server 无缝集成，实现智能流管理

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         公网环境                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     cp_server                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │  Web 管理台  │  │  REST API   │  │  WebSocket  │     │   │
│  │  │  (Django)   │  │  (Django)   │  │ (Channels)  │     │   │
│  │  └─────────────┘  └─────────────┘  └──────┬──────┘     │   │
│  │                                           │             │   │
│  │  ┌─────────────┐  ┌─────────────┐         │             │   │
│  │  │   SQLite    │  │   cp_zlm    │◄────────┤             │   │
│  │  │  (数据库)   │  │ (流媒体)    │         │             │   │
│  │  └─────────────┘  └─────────────┘         │             │   │
│  └────────────────────────────────────────────┼─────────────┘   │
│                                               │                 │
└───────────────────────────────────────────────┼─────────────────┘
                                                │ WebSocket
                                                │ (主动连接)
┌───────────────────────────────────────────────┼─────────────────┐
│                         内网环境               │                 │
│  ┌────────────────────────────────────────────┼─────────────┐   │
│  │                   rebekah_admin            │             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────┴──────┐     │   │
│  │  │  AI 分析    │  │  视频采集   │  │cluster_client│     │   │
│  │  │  (算法)     │  │  (摄像头)   │  │ (WebSocket)  │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 核心流程

1. **节点注册流程**：rebekah_admin 启动时连接到 cp_server，发送注册消息，cp_server 验证并存储节点信息
2. **按需推流流程**：用户点击视频播放，cp_zlm 触发回调，cp_server 发送推流命令，rebekah_admin 开始推流
3. **报警处理流程**：rebekah_admin 产生报警，cp_server 通过 WebSocket 获取报警信息，存储并显示在管理后台

---

## 快速开始

### 环境要求

- **Python**: 3.8+（推荐 3.9 或 3.10）
- **操作系统**: Windows 10+（64位）、Linux (Ubuntu 18.04+ / CentOS 7+)、macOS 10.14+（64位）
- **Rebekah 版本**: v5.002+（仅支持此版本及以后）
- **网络要求**: 管理端需要公网或局域网可访问的 IP 地址
- **硬件要求**: 管理端至少 2GB 内存，10GB 磁盘空间

### 安装步骤

#### 1. 克隆项目

**从 GitHub 克隆：**
```bash
git clone https://github.com/beixiaocai/cluster_platform.git
cd cluster_platform
```

**从 Gitee 克隆：**
```bash
git clone https://gitee.com/Vanishi/cluster_platform.git
cd cluster_platform
```

#### 2. 安装 cp_server 依赖

```bash
cd cp_server

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. 配置 cp_server

编辑 `cp_server/config.json`，根据实际需求修改配置：

```json
{
    "host": "192.168.1.12",
    "logDebug": true,
    "adminPort": 9824,
    "mediaRtspPort": 9854,
    "mediaHttpPort": 9826,
    "mediaSecret": "XcNvs2025zlmzs0aA9ajn7UiOWi",
    "wsToken": "cp_server_safe_key_2026",
    "install": "D:\\project\\rebekah\\cluster_platform\\cp_server",
    "isEnableLoginCaptcha": false,
    "fontPath": "D:\\project\\rebekah\\cluster_platform\\cp_server\\static\\upload\\fonts\\tsimhei.ttf",
    "uploadDir": "D:\\project\\rebekah\\cluster_platform\\cp_server\\static\\upload",
    "storageDir": "D:\\project\\rebekah\\cluster_platform\\cp_server\\static\\storage"
}
```


#### 4. 直接使用内置账号登录

系统已内置管理员账号，无需单独初始化数据库和创建用户：
- **用户名**: admin
- **密码**: admin888

#### 5. 启动 cp_zlm（流媒体服务器）

**Windows:**
```bash
cd cp_zlm/bin.x86.windows10
cp_zlm.exe
```

**Linux x86:**
```bash
cd cp_zlm/bin.x86.gcc9.4
chmod +x cp_zlm
./cp_zlm
```

**Linux ARM:**
```bash
cd cp_zlm/bin.arm.gcc9.4
chmod +x cp_zlm
./cp_zlm
```

#### 6. 启动 cp_server

**开发环境：**
```bash
cd cp_server
python manage.py runserver 0.0.0.0:9824
```

**生产环境：**
```bash
cd cp_server
# 使用 Gunicorn 启动
pip install gunicorn uvicorn
GUNICORN_CMD_ARGS="--bind=0.0.0.0:9824 --workers=4 --worker-class=uvicorn.workers.UvicornWorker" gunicorn framework.asgi:application
```



#### 7. 访问管理后台

打开浏览器访问：http://localhost:9824

使用内置账号登录：
- **用户名**: admin
- **密码**: admin888

---

## 配置说明

### cp_server 配置 (config.json)

| 参数 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `host` | string | 服务器主机地址 | `192.168.1.12` |
| `logDebug` | boolean | 是否开启调试日志 | `true` |
| `adminPort` | int | Web 管理端口 | `9824` |
| `mediaRtspPort` | int | ZLMediaKit RTSP 端口 | `9854` |
| `mediaHttpPort` | int | ZLMediaKit HTTP 端口 | `9826` |
| `mediaSecret` | string | ZLMediaKit API 密钥 | `XcNvs2025zlmzs0aA9ajn7UiOWi` |
| `wsToken` | string | WebSocket 认证 Token | `cp_server_safe_key_2026` |
| `install` | string | 安装路径 | `D:\project\rebekah\cluster_platform\cp_server` |
| `isEnableLoginCaptcha` | boolean | 是否启用登录验证码 | `false` |
| `fontPath` | string | 字体文件路径 | `D:\project\rebekah\cluster_platform\cp_server\static\upload\fonts\tsimhei.ttf` |
| `uploadDir` | string | 上传文件目录 | `D:\project\rebekah\cluster_platform\cp_server\static\upload` |
| `storageDir` | string | 存储文件目录 | `D:\project\rebekah\cluster_platform\cp_server\static\storage` |


## 部署指南

### 多环境部署

- **开发环境**：`DEBUG = True`，详细日志，使用 `python manage.py runserver 9824` 启动
- **测试环境**：`DEBUG = False`，详细日志，使用 Gunicorn + Nginx 启动
- **生产环境**：`DEBUG = False`，生产日志，使用 Gunicorn + Nginx + systemd 启动，建议使用 PostgreSQL 或 MySQL

### 大规模部署建议

1. **服务器选择**：管理端至少 4 核 CPU，8GB 内存，50GB 磁盘
2. **网络规划**：管理端需要公网 IP 或端口映射，节点端需要能够访问管理端的 WebSocket 服务
3. **负载均衡**：对于大规模部署，考虑使用负载均衡器
4. **高可用**：配置主备管理节点，使用共享存储，实现自动故障转移
5. **存储方案**：报警图片和视频使用对象存储，配置 CDN 加速静态资源

---

## 常见问题

### 连接问题

- **节点无法连接到 cp_server**：检查 Token 配置、版本兼容性、网络连通性、服务器状态
- **WebSocket 连接频繁断开**：检查网络稳定性、心跳配置、服务器负载、防火墙设置

### 视频流问题

- **视频无法播放**：检查流媒体服务、配置一致性、回调配置、节点状态、流名称、网络带宽
- **推流失败**：检查节点状态、流名称、推流权限、网络连接、节点日志、流媒体服务器
- **视频卡顿或延迟**：检查网络带宽、服务器性能、编码设置、播放器缓存、流媒体服务器配置

### 报警问题

- **报警图片无法显示**：确保节点连接正常、报警图片路径正确、文件存在、文件大小适中、网络连接稳定
- **报警信息延迟或丢失**：检查网络延迟、服务器负载、WebSocket 连接、节点状态

### 系统问题

- **系统运行缓慢**：检查服务器资源、数据库性能、并发连接、日志级别、静态资源优化
- **数据库操作缓慢**：考虑使用 PostgreSQL，优化数据库索引，优化查询语句，调整连接池设置，定期清理数据

---

## 技术栈

### 后端

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **Web框架** | Django | 5.0.4 | 后台管理服务 |
| **WebSocket** | Channels | 4.1.0 | 实时通信支持 |
| **数据库** | SQLite | - | 轻量级数据存储 |
| **异步支持** | Daphne | 4.1.2 | ASGI 服务器 |
| **静态文件** | WhiteNoise | 6.9.0 | 静态文件处理 |
| **流媒体** | ZLMediaKit | - | 高性能流媒体服务 |

### 前端

| 组件 | 技术 | 用途 |
|------|------|------|
| **模板引擎** | Django Templates | 页面渲染 |
| **样式框架** | Bootstrap 5 | UI 组件 |
| **播放器** | flv.js / hls.js | 视频播放 |
| **JavaScript** | jQuery | DOM 操作 |
| **图标** | Font Awesome | 图标库 |
| **图表** | ECharts | 数据可视化 |

---

## 与主项目的关系

cluster_platform 是 Rebekah 智能视频分析平台的集群管理模块，用于：

1. **集中管理**: 统一管理多个 rebekah_admin 节点，实现集群化管理
2. **跨网络部署**: 支持公网部署管理端，内网部署节点端，无需 VPN
3. **按需推流**: 用户查看视频时才推流，节省带宽和服务器资源
4. **报警汇聚**: 汇聚各节点报警信息，统一查看和处理
5. **远程控制**: 通过 WebSocket 远程控制节点，实现远程管理
6. **版本控制**: 确保节点版本兼容性，只支持 Rebekah v5.002+ 版本

---

## 开源地址

- GitHub: https://github.com/beixiaocai/cluster_platform
- Gitee: https://gitee.com/Vanishi/cluster_platform

## 联系方式

- GitHub Issues: https://github.com/beixiaocai/cluster_platform/issues
- Gitee Issues: https://gitee.com/Vanishi/cluster_platform/issues
