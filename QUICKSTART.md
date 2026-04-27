# AI攻防靶场管理系统 - 快速启动指南

## 系统要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ (可选，系统支持无数据库模式运行)
- Docker Desktop (可选，用于靶场环境)

## 快速启动

### 方式一：使用启动脚本（Windows）

双击运行 `start.bat` 文件，脚本会自动：
1. 检查环境依赖
2. 安装后端依赖
3. 安装前端依赖
4. 显示启动命令

### 方式二：手动启动

#### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 安装前端依赖

```bash
cd frontend
npm install
```

#### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cd backend
copy .env.example .env
```

主要配置项：
- `ZHIPUAI_API_KEY`: 智谱AI API密钥（用于AI分析功能）
- `DB_HOST/DB_USER/DB_PASSWORD/DB_DATABASE`: 数据库连接配置
- `SECRET_KEY/JWT_SECRET_KEY`: 安全密钥

#### 4. 启动后端服务

```bash
cd backend
python -m app.app
```

后端服务地址：http://localhost:5000

#### 5. 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务地址：http://localhost:3000

## 默认账户

系统启动后会自动创建默认管理员账户：
- 用户名：`admin`
- 密码：`admin123`

**注意：生产环境请及时修改默认密码！**

## 功能模块

### 1. 仪表盘 (Dashboard)
- 系统状态概览
- 实时统计数据
- 健康度监控
- 告警信息展示

### 2. 环境管理 (EnvManage)
- 靶场环境创建/删除
- Docker容器管理
- 环境状态监控
- 端口映射配置

### 3. 攻击面板 (AttackPanel)
- 攻击任务管理
- 多种攻击类型支持
- 攻击进度监控
- 攻击日志查看

### 4. 防御面板 (DefensePanel)
- 防御策略配置
- 防火墙规则管理
- IDS/IPS配置
- WAF规则设置

### 5. 日志管理 (Logs)
- 系统日志查看
- 日志筛选过滤
- 日志导出功能
- 日志统计分析

### 6. AI决策 (AiDecision)
- AI安全态势分析
- 智能威胁检测
- 自动防御建议
- AI对话交互

### 7. 网络拓扑 (Topology)
- 网络拓扑可视化
- 节点状态监控
- Ping/SSH测试
- 网络扫描功能

## API接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户信息

### 统计接口
- `GET /api/stats` - 获取统计数据
- `GET /api/dashboard` - 获取仪表盘数据
- `GET /api/health` - 健康检查

### 环境接口
- `GET /api/targets/` - 获取环境列表
- `POST /api/targets/` - 创建环境
- `POST /api/targets/{id}/start` - 启动环境
- `POST /api/targets/{id}/stop` - 停止环境

### 攻击接口
- `GET /api/attacks/` - 获取攻击列表
- `POST /api/attacks/` - 创建攻击任务
- `POST /api/attacks/{id}/start` - 启动攻击
- `POST /api/attacks/{id}/stop` - 停止攻击

### 防御接口
- `GET /api/defenses/` - 获取防御列表
- `POST /api/defenses/` - 创建防御策略
- `POST /api/defenses/{id}/enable` - 启用防御
- `POST /api/defenses/{id}/disable` - 禁用防御

### AI接口
- `POST /api/ai/summary` - 生成AI分析报告
- `POST /api/ai/analyze` - 分析威胁
- `POST /api/ai/apply-defense` - 应用AI防御建议
- `GET /api/ai/recommendations` - 获取安全建议

### 拓扑接口
- `GET /api/topology/` - 获取拓扑数据
- `POST /api/topology/ping` - Ping测试
- `POST /api/topology/ssh` - SSH连接
- `POST /api/topology/scan` - 网络扫描

## 常见问题

### Q: 后端启动失败？
A: 检查Python版本和依赖安装，确保已安装所有requirements.txt中的包。

### Q: 前端无法连接后端？
A: 确认后端服务已启动，检查vite.config.js中的代理配置。

### Q: 数据库连接失败？
A: 检查MySQL服务是否运行，确认.env中的数据库配置正确。

### Q: AI功能不工作？
A: 确认已配置有效的智谱AI API密钥，系统支持无API密钥的模拟模式运行。

## 技术支持

如有问题，请查看项目README.md获取更多信息。