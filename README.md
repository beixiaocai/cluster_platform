# Cluster Platform - 集群管理平台

<div align="center">

![Version](https://img.shields.io/badge/version-1.009-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Django](https://img.shields.io/badge/django-5.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**轻量级视频分析集群管理平台**

[功能特性](#功能特性) • [快速开始](#快速开始) • [配置说明](#配置说明) • [常见问题](HELP.md) • [更新日志](#更新日志)

</div>

---

* 体验地址：http://47.110.138.209:9824  账号：admin 密码： admin888

## 项目简介

cluster_platform 是专为 视频行为分析系统(rebekah) v5.002+ 设计的集群管理平台，支持统一管理多个 rebekah 节点。

### 核心特性

- 🚀 **轻量级架构**：支持 MySQL/SQLite，灵活选择数据库
- 🌐 **跨网络部署**：公网部署管理端，内网部署节点端
- ⚡ **WebSocket 通信**：所有 API 通过 WebSocket 转发，支持公网管理内网节点
- 📹 **流媒体集成**：内置 ZLMediaKit，支持多协议和按需推流
- 🔐 **安全认证**：Token 认证 + API 安全密钥
- 💓 **心跳监控**：实时监控节点状态，支持心跳历史记录查询

---

## 目录结构

```
cluster_platform/
├── cp_server/                 # 管理中心服务
│   ├── app/                   # 应用模块
│   ├── framework/             # Django 配置
│   ├── static/                # 静态资源
│   ├── templates/             # 模板文件
│   ├── config-windows.json    # Windows配置文件
│   ├── config-linux.json      # Linux配置文件
│   └── manage.py              # Django 管理脚本
└── README.md
```

---

## 功能特性

### 平台功能
- 控制面板、节点管理、用户管理、在线流、启动配置

### 节点功能
- 报警管理、视频管理、布控管理、音频管理、人脸管理、计划任务、算法相关、录像管理

---

## 架构设计

```
┌─────────────────────────────────┐
│          公网环境                │
│  ┌───────────────────────────┐  │
│  │        cp_server          │  │
│  │  Web管理台 - REST API - WebSocket │
│  │  MySQL - cp_zlm          │  │
│  └───────────────────────────┘  │
└───────────────┬─────────────────┘
                │ WebSocket
┌───────────────┴─────────────────┐
│          内网环境                │
│  ┌───────────────────────────┐  │
│  │        rebekah            │  │
│  │  AI分析 - 视频采集 - cluster_client │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

---

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+ 或 SQLite
- Rebekah v5.002+

### 安装步骤

#### 1. 克隆项目 & 安装依赖

```bash
git clone https://github.com/beixiaocai/cluster_platform.git
cd cluster_platform/cp_server
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2. 数据库配置（MySQL）

```sql
创建数据库 cluster_platform
导入 cluster_platform.sql
```

编辑 `cp_server/framework/settings.py`：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cluster_platform',
        'USER': 'root',
        'PASSWORD': 'pwd123456',
        'HOST': '192.168.1.6',
        'PORT': '3306',
    }
}
```


#### 3. 配置 & 启动

编辑 `cp_server/config-xxx.json`，然后：
```bash
# 启动流媒体服务器
cd cp_zlm/bin.x86.windows10
cp_zlm.exe

# 启动管理中心
cd cp_server
python manage.py runserver 0.0.0.0:9824
```

访问：http://localhost:9824，默认账号 `admin` / `admin888`

---

## 配置说明

### config-xxx.json 参数
* 请根据自己的平台选择config-windows.json 或 config-linux.json
* 将选择的config-xxx.json 改名为 config.json

---

## 技术栈

- Django 5.0, Channels 4.1, Daphne 4.1
- MySQL / SQLite
- ZLMediaKit
- Bootstrap 5 + jQuery

---

## 更新日志

### v1.009 (2026-04-28)

**录像播放器升级**
- 升级为二级时间轴：一级显示24小时概览，二级显示小时内20个3分钟切片
- 支持部分录像渐变色显示，新增"部分录像"图例
- 选中小时/播放切片高亮标识
- 连续播放间隔从60秒对齐为180秒（与后端切片一致）

**报警详情修复**
- 修复报警详情弹框只显示一张图片的问题（节点编号含`.`时路径分割错误）

### v1.007 (2026-03-31)

**UI 全面升级**
- 新增平台报警管理功能
- 首页控制面板美化，现代化卡片设计
- 配置页面重新设计，与首页风格统一
- 侧边栏颜色风格优化，深灰蓝+蓝色系
- 登录页面调整，与系统风格保持一致
- 9个统计卡片统一高度和布局，图标缩小优化

**WebSocket 深度优化**
- 修复 15+ 个功能和性能 bug
- 使用 RLock 替代 Lock 解决死锁问题
- 优化心跳机制，批量写入减少数据库压力
- 命令队列增加大小限制，防止内存泄漏

**数据库 & 路由**
- 默认从 SQLite 切换到 MySQL

---

## 开源地址

- GitHub: https://github.com/beixiaocai/cluster_platform
- Gitee: https://gitee.com/Vanishi/cluster_platform
