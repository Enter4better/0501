# 网络安全靶场系统 - 快速启动指南

## 系统要求
- Python 3.8+
- Node.js 14+
- Docker
- Git

## 安装步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd cyber-range
```

### 2. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装前端依赖
```bash
cd ../frontend
npm install
```

### 4. 启动系统
```bash
# 启动后端
cd backend
python run.py

# 启动前端
cd frontend
npm run dev
```

## 系统功能概览

### 攻击模拟
- 访问 `/attack` 进行攻击模拟
- 选择攻击类型和目标
- 配置攻击参数并执行

### 防御系统
- 访问 `/defense` 配置防御策略
- 监控系统安全状态
- 响应安全事件

### 靶场管理
- 访问 `/env` 管理靶场环境
- 创建、启动、停止和删除靶场
- 监控靶场资源使用情况

### 日志分析
- 访问 `/logs` 查看系统日志
- 分析攻击和防御活动
- 生成安全报告

### 网络拓扑
- 访问 `/topology` 查看网络拓扑
- 可视化展示网络结构和连接关系

## API接口
系统提供完整的RESTful API接口，详见 `API_REFERENCE.md` 文档。

## 故障排除
- 如果Docker容器无法启动，请检查Docker服务是否运行
- 如遇其他问题，请查看系统日志