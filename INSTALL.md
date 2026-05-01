# 网络安全靶场系统 - 安装指南

## 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, 或 Linux (Ubuntu 18.04+, CentOS 7+)
- **Python**: 3.8 或更高版本
- **Node.js**: 14 或更高版本
- **Docker**: 最新稳定版本
- **内存**: 至少 4GB RAM (推荐 8GB)
- **磁盘空间**: 至少 10GB 可用空间
- **Git**: 用于克隆项目仓库

## 安装步骤

### 1. 环境准备

#### 安装 Python
- 从 [Python官网](https://www.python.org/downloads/) 下载并安装 Python 3.8+
- 确保在安装时勾选 "Add Python to PATH"

#### 安装 Node.js
- 从 [Node.js官网](https://nodejs.org/) 下载并安装 LTS 版本
- 验证安装：`node --version` 和 `npm --version`

#### 安装 Docker
- 从 [Docker官网](https://docs.docker.com/get-docker/) 下载并安装
- 启动 Docker 服务
- 验证安装：`docker --version`

#### 安装 Git
- 从 [Git官网](https://git-scm.com/downloads) 下载并安装
- 验证安装：`git --version`

### 2. 克隆项目
```bash
git clone <repository-url>
cd cyber-range
```

### 3. 后端配置

#### 安装 Python 依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 配置环境变量
复制 `.env.example` 文件并重命名为 `.env`：
```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：
- `SECRET_KEY`: 用于会话加密的密钥
- `DATABASE_URL`: 数据库连接字符串 (默认使用SQLite)
- `DOCKER_HOST`: Docker守护进程地址 (如果使用远程Docker)

### 4. 前端配置

#### 安装 Node.js 依赖
```bash
cd frontend
npm install
```

#### 配置前端环境
编辑 `vite.config.js` 中的后端API代理配置：
```javascript
export default {
  // ...
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    }
  }
}
```

### 5. 数据库初始化
系统使用SQLite作为默认数据库，无需额外配置。首次运行时会自动创建数据库文件。

### 6. 启动系统

#### 启动后端服务
```bash
cd backend
python run.py
```

#### 启动前端服务
```bash
cd frontend
npm run dev
```

### 7. 访问系统
- 前端地址: http://localhost:3000
- 后端API: http://localhost:5000
- 默认账户: admin/admin123

## 功能模块

### 攻击模拟模块
- 支持16种标准攻击类型
- 参数化攻击配置
- 实时攻击状态监控

### 防御系统模块
- 多层防御机制
- 实时威胁检测
- 防御策略配置

### 靶场管理模块
- 靶场环境创建与管理
- Docker容器生命周期管理
- 资源监控与清理

### 日志分析模块
- 攻击日志记录
- 防御日志记录
- 系统活动日志

### 网络拓扑模块
- 网络结构可视化
- 节点状态监控
- 连接关系展示

## 验证安装

### 1. 检查服务状态
- 确认后端服务在 http://localhost:5000 正常运行
- 确认前端服务在 http://localhost:3000 正常运行
- 确认Docker服务正在运行

### 2. 测试功能
- 尝试登录系统 (默认账户: admin/admin123)
- 创建一个靶场环境
- 尝试发起一次攻击
- 查看系统日志

## 常见问题

### Q: 后端服务启动失败？
A: 检查Python版本是否为3.8+，确认requirements.txt中的依赖已正确安装。

### Q: 前端无法连接后端？
A: 检查vite.config.js中的代理配置，确认后端服务正在运行。

### Q: Docker容器无法创建？
A: 检查Docker服务是否启动，确认有足够的磁盘空间。

### Q: 数据库连接错误？
A: 确认SQLite文件路径正确，检查是否有足够的文件系统权限。

### Q: 端口被占用？
A: 修改后端端口（在run.py中）或前端端口（在vite.config.js中）。

## 系统配置

### 性能调优
- 增加Docker的内存分配（推荐至少2GB）
- 调整Python的垃圾回收参数
- 优化数据库连接池大小

### 安全配置
- 修改默认账户密码
- 配置HTTPS（生产环境）
- 设置适当的防火墙规则

## 卸载

### 1. 停止服务
```bash
# 停止前端 (Ctrl+C)
# 停止后端 (Ctrl+C)
```

### 2. 清理Docker容器
```bash
# 停止所有容器
docker stop $(docker ps -aq)
# 删除所有容器
docker rm $(docker ps -aq)
```

### 3. 删除项目
```bash
rm -rf cyber-range
```

## 技术支持
如遇到安装问题，请检查系统要求是否满足，确认所有依赖已正确安装。如有其他问题，请联系技术支持。