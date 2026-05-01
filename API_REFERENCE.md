# 网络安全靶场系统 - API接口参考

## 概述
网络安全靶场系统提供了一套完整的API接口，用于管理攻击、防御、靶场环境等功能。所有接口均基于RESTful设计原则，使用JSON格式进行数据交换。

## 认证
系统使用JWT Token进行身份认证。在访问受保护的API接口时，需要在请求头中添加：
```
Authorization: Bearer <your-jwt-token>
```

## 接口列表

### 认证相关
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/profile` - 获取用户信息

### 攻击管理
- `GET /api/attacks/types` - 获取攻击类型列表
- `POST /api/attacks/start` - 开始攻击
- `GET /api/attacks/status` - 获取攻击状态
- `GET /api/attacks/history` - 获取攻击历史

### 防御管理
- `GET /api/defense/list` - 获取防御策略列表
- `POST /api/defense/activate` - 激活防御策略
- `GET /api/defense/status` - 获取防御状态
- `POST /api/defense/configure` - 配置防御策略

### 靶场环境
- `GET /api/env/list` - 获取靶场环境列表
- `POST /api/env/create` - 创建靶场环境
- `POST /api/env/start` - 启动靶场环境
- `POST /api/env/stop` - 停止靶场环境
- `DELETE /api/env/delete` - 删除靶场环境

### 统计数据
- `GET /api/stats/attacks` - 获取攻击统计数据
- `GET /api/stats/defenses` - 获取防御统计数据
- `GET /api/stats/threats` - 获取威胁统计数据

### 日志管理
- `GET /api/logs/activity` - 获取活动日志
- `GET /api/logs/attacks` - 获取攻击日志
- `GET /api/logs/defenses` - 获取防御日志
- `GET /api/logs/system` - 获取系统日志

### 网络拓扑
- `GET /api/topology/current` - 获取当前网络拓扑
- `POST /api/topology/update` - 更新网络拓扑
- `GET /api/topology/history` - 获取拓扑变更历史

## 数据模型

### 攻击类型
```json
{
  "id": "sql_injection",
  "name": "SQL注入",
  "category": "web_vulnerability",
  "description": "通过注入恶意SQL语句来操纵数据库",
  "severity": "high"
}
```

### 防御策略
```json
{
  "id": "waf_rule_001",
  "name": "WAF规则",
  "type": "firewall",
  "description": "Web应用防火墙规则",
  "config": {
    "rules": ["sql_injection", "xss", "csrf"],
    "action": "block"
  }
}
```

### 靶场环境
```json
{
  "id": "env_001",
  "name": "Web应用靶场",
  "status": "running",
  "created_at": "2024-01-01T00:00:00Z",
  "containers": [
    {
      "id": "container_001",
      "name": "web_server",
      "image": "vulnerable_web_app:latest",
      "ports": [80, 443],
      "status": "running"
    }
  ]
}
```

### 日志条目
```json
{
  "id": "log_001",
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "info",
  "source": "attack_module",
  "event": "attack_started",
  "details": {
    "attack_type": "sql_injection",
    "target": "web_server_001",
    "parameters": {
      "payload": "' OR 1=1 --",
      "intensity": "medium"
    }
  }
}
```

## 错误处理
所有API接口在发生错误时会返回以下格式的错误信息：
```json
{
  "status": "error",
  "code": 400,
  "msg": "错误描述信息"
}
```

## 示例请求
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 示例响应
```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}