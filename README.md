# AI Security Range - 智能攻防靶场

> 基于 Vue 3 + Flask + Docker 的网络安全攻防演练平台

## 快速启动

### 1. 前端

```bash
cd frontend
npm install
npm run dev       # 开发模式 → http://localhost:3000
npm run build      # 生产构建
```

### 2. 后端

```bash
cd backend
pip install -r requirements.txt

# 配置智谱AI（可选，不配置则使用内置演示数据）
cp .env.example .env
# 编辑 .env，填入 ZHIPUAI_API_KEY

python app.py     # → http://localhost:5000
```

### 3. Docker（靶场管理功能）

确保 **Docker Desktop** 已启动（仅 Windows/macOS），Linux 用 `dockerd`。

## 功能模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 控制台 | `/` | 实时攻击/防御状态、拓扑图 |
| 攻击模拟 | `/attack` | 17种攻击类型、参数配置 |
| 防御中心 | `/defense` | WAF/IDS/IPS规则管理 |
| 网络拓扑 | `/topology` | SVG动态拓扑图 |
| 日志监控 | `/logs` | 彩色分级日志流 |
| AI决策 | `/ai` | 智谱GLM-4安全分析报告 |
| 靶场管理 | `/env` | Docker容器CRUD |
| 登录 | `/login` | 用户认证 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Vue 3 + Vite 5 |
| UI 组件 | Element Plus 2 |
| 后端框架 | Flask 3 |
| 容器管理 | Docker SDK |
| AI 模型 | 智谱 GLM-4 (`zhipuai`) |
| 样式 | 自定义科技朋克 CSS 变量系统 |

## 设计风格

- **主题**：紫色科技朋克
- **主色**：`#00e5ff` 电光青 + `#8b2ce6` 紫罗兰
- **背景**：`#0a0a14` 深紫黑
- **字体**：Orbitron（标题）+ Rajdhani（正文）+ JetBrains Mono（代码）
