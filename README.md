# Cluster Platform - 集群管理平台

<div align="center">

![Version](https://img.shields.io/badge/version-1.002-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Django](https://img.shields.io/badge/django-5.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**轻量级视频分析集群管理平台**

[功能特性](#功能特性) • [快速开始](#快速开始) • [配置说明](#配置说明)

</div>

---

## 项目简介

Cluster Platform 是专为 Rebekah 视频行为分析系统 v5.002+ 设计的集群管理平台，支持统一管理多个 rebekah_admin 节点。

### 核心特性

- 🚀 **轻量级架构**：基于 SQLite，无需额外数据库
- 🌐 **跨网络部署**：公网部署管理端，内网部署节点端
- ⚡ **WebSocket 通信**：所有 API 通过 WebSocket 转发，支持公网管理内网节点
- 📹 **流媒体集成**：内置 ZLMediaKit，支持多协议和按需推流
- 🔐 **安全认证**：Token 认证 + API 安全密钥

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
│   └── manage.py              # Django 管理脚本
│
├── cp_zlm/                    # 流媒体服务器
│   ├── bin.x86.windows10/     # Windows 可执行文件
│   ├── bin.x86.gcc9.4/        # Linux x86 可执行文件
│   └── bin.arm.gcc9.4/        # Linux ARM 可执行文件
│
└── README.md
```

---

## 功能特性

### 平台功能
- **控制面板** - 系统首页，展示节点状态、流媒体数据等概览
- **平台节点管理** - 管理所有注册的 rebekah_admin 节点
- **平台用户管理** - 管理平台登录用户
- **平台在线流** - 查看所有节点的在线流信息
- **平台启动配置** - 配置平台运行参数

### 节点功能（通过 WebSocket 转发到各节点执行）
- **报警管理** - 查看和管理各节点报警信息
- **视频管理** - 管理视频流，支持播放、转发控制、云台操作
- **布控管理** - 布控任务管理
- **音频管理** - 音频文件管理
- **人脸管理** - 人脸库管理
- **计划任务** - 定时任务管理
- **算法测试** - 算法效果测试
- **业务算法管理** - 算法流程编排
- **基础算法管理** - 基础算法配置
- **行为算法管理** - 行为识别算法
- **大模型管理** - LLM 模型配置
- **录像计划管理** - 录像计划配置
- **录像播放器** - 历史录像回放

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                         公网环境                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     cp_server                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │  Web 管理台  │  │  REST API   │  │  WebSocket  │     │   │
│  │  └─────────────┘  └─────────────┘  └──────┬──────┘     │   │
│  │                                           │             │   │
│  │  ┌─────────────┐  ┌─────────────┐         │             │   │
│  │  │   SQLite    │  │   cp_zlm    │◄────────┤             │   │
│  │  └─────────────┘  └─────────────┘         │             │   │
│  └────────────────────────────────────────────┼─────────────┘   │
└───────────────────────────────────────────────┼─────────────────┘
                                                │ WebSocket
                                                │ (主动连接)
┌───────────────────────────────────────────────┼─────────────────┐
│                         内网环境               │                 │
│  ┌────────────────────────────────────────────┼─────────────┐   │
│  │                   rebekah_admin            │             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────┴──────┐     │   │
│  │  │  AI 分析    │  │  视频采集   │  │cluster_client│     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 环境要求

- **Python**: 3.8+（推荐 3.9 或 3.10）
- **操作系统**: Windows 10+ / Linux (Ubuntu 18.04+) / macOS 10.14+
- **Rebekah 版本**: v5.002+

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/beixiaocai/cluster_platform.git
cd cluster_platform
```

#### 2. 安装依赖

```bash
cd cp_server
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. 配置 cp_server

编辑 `cp_server/config.json`：

```json
{
    "host": "192.168.1.12",
    "safe": "x20y17W1X2SHI3xDA4MEI",
    "logDebug": true,
    "adminPort": 9824,
    "mediaRtspPort": 9854,
    "mediaHttpPort": 9826,
    "mediaSecret": "cp2026zlmzs0aA9ajn7UiOWie",
    "wsToken": "cp_server_safe_key_2026",
    "install": "D:\\project\\rebekah\\cluster_platform\\cp_server",
    "isEnableLoginCaptcha": false,
    "fontPath": "D:\\project\\rebekah\\cluster_platform\\cp_server\\static\\upload\\fonts\\tsimhei.ttf",
    "uploadDir": "D:\\project\\rebekah\\cluster_platform\\cp_server\\static\\upload",
    "storageTempDir": "D:\\project\\rebekah\\cluster_platform\\cp_server\\static\\storage\\temp"
}
```

#### 4. 启动服务

```bash
# 启动 cp_zlm（流媒体服务器）
cd cp_zlm/bin.x86.windows10
cp_zlm.exe

# 启动 cp_server（管理中心）
cd cp_server
python manage.py runserver 0.0.0.0:9824
```

#### 5. 访问管理后台

打开浏览器访问：http://localhost:9824

默认账号：`admin` / `admin888`

---

## 配置说明

### cp_server 配置 (config.json)

| 参数 | 类型 | 说明 |
|------|------|------|
| `host` | string | 服务器主机地址 |
| `safe` | string | API 安全密钥，用于开放接口验证 |
| `logDebug` | boolean | 是否开启调试日志 |
| `adminPort` | int | Web 管理端口 |
| `mediaRtspPort` | int | ZLMediaKit RTSP 端口 |
| `mediaHttpPort` | int | ZLMediaKit HTTP 端口 |
| `mediaSecret` | string | ZLMediaKit API 密钥 |
| `wsToken` | string | WebSocket 认证 Token |
| `install` | string | 安装路径 |
| `isEnableLoginCaptcha` | boolean | 是否启用登录验证码 |
| `fontPath` | string | 字体文件路径 |
| `uploadDir` | string | 上传文件目录 |
| `storageTempDir` | string | 临时存储目录 |

---

## 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| Web框架 | Django 5.0 | 后台管理服务 |
| WebSocket | Channels 4.1 | 实时通信支持 |
| 数据库 | SQLite | 轻量级数据存储 |
| 异步支持 | Daphne 4.1 | ASGI 服务器 |
| 流媒体 | ZLMediaKit | 高性能流媒体服务 |
| 前端 | Bootstrap 5 + jQuery | UI 组件 |

---

## 开源地址

- GitHub: https://github.com/beixiaocai/cluster_platform
- Gitee: https://gitee.com/Vanishi/cluster_platform
