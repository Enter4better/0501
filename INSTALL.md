# AI攻防靶场管理系统 - 安装指南

## 环境要求

### 必需软件

1. **Node.js 16+** ✅ (已安装 v24.14.0)
2. **Python 3.8+** ❌ (需要安装)

---

## Python 安装步骤

### Windows 安装 Python

#### 方式一：官网下载（推荐）

1. 访问 Python 官网：https://www.python.org/downloads/
2. 下载 Python 3.10 或 3.11 版本（推荐 3.11）
3. 运行安装程序
4. **重要**：勾选 "Add Python to PATH" 选项
5. 点击 "Install Now" 完成安装

#### 方式二：Microsoft Store

1. 打开 Microsoft Store
2. 搜索 "Python 3.11"
3. 点击安装

#### 方式三：使用 winget（Windows 10/11）

```powershell
winget install Python.Python.3.11
```

### 验证安装

安装完成后，**重新打开终端**，运行：

```powershell
python --version
pip --version
```

---

## 项目启动步骤

### 1. 安装后端依赖

```powershell
cd d:\AI-security-range\backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```powershell
# 复制配置文件
copy .env.example .env
# 编辑 .env 文件，配置数据库和API密钥
```

### 3. 启动后端服务

```powershell
cd d:\AI-security-range\backend
python -m app.app
```

后端服务地址：http://localhost:5000

### 4. 启动前端服务（已启动 ✅）

```powershell
cd d:\AI-security-range\frontend
npm run dev
```

前端服务地址：http://localhost:3000

---

## 数据库配置

系统支持两种运行模式：
- **无数据库模式**：使用内存模拟数据，适合快速体验和演示
- **数据库模式**：使用 MySQL 存储数据，适合生产环境和完整功能

### 方式一：无数据库模式（推荐新手）

无需安装数据库，系统启动后会自动使用模拟数据。直接启动后端即可：

```powershell
cd d:\AI-security-range\backend
python -m app.app
```

### 方式二：MySQL 数据库模式

#### 1. 安装 MySQL

**Windows 安装 MySQL：**

##### 方式A：官网下载（推荐）
1. 访问 MySQL 官网：https://dev.mysql.com/downloads/mysql/
2. 选择 Windows 版本下载
3. 运行安装程序，选择 "Developer Default" 或 "Server only"
4. 设置 root 密码（建议设置简单密码如 `root123` 用于开发）
5. 完成安装

##### 方式B：使用 winget
```powershell
winget install Oracle.MySQL
```

##### 方式C：使用 Chocolatey
```powershell
choco install mysql -y
```

#### 2. 启动 MySQL 服务

安装后确保 MySQL 服务正在运行：

```powershell
# 查看服务状态
net start | findstr MySQL

# 如果未启动，手动启动
net start MySQL80
# 或
net start MySQL
```

#### 3. 创建数据库

使用 MySQL 命令行或图形工具创建数据库：

**命令行方式：**
```powershell
# 登录 MySQL（密码为安装时设置的密码）
mysql -u root -p
```

在 MySQL 命令行中执行：
```sql
-- 创建数据库
CREATE DATABASE ai_security_range CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户（可选，推荐）
CREATE USER 'ai_range'@'localhost' IDENTIFIED BY 'ai_range123';
GRANT ALL PRIVILEGES ON ai_security_range.* TO 'ai_range'@'localhost';
FLUSH PRIVILEGES;

-- 验证数据库创建成功
SHOW DATABASES;

-- 退出
EXIT;
```

**图形工具方式（MySQL Workbench）：**
1. 打开 MySQL Workbench
2. 连接到本地 MySQL 服务器
3. 点击 "Create a new schema"
4. 输入名称：`ai_security_range`
5. 设置字符集：`utf8mb4`
6. 点击 Apply

#### 4. 配置项目数据库连接

编辑 `backend/.env` 文件：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_DATABASE=ai_security_range

# 如果创建了专用用户
# DB_USER=ai_range
# DB_PASSWORD=ai_range123
```

#### 5. 初始化数据库表结构

启动后端服务时，系统会自动创建所需的表结构：

```powershell
cd d:\AI-security-range\backend
python -m app.app
```

首次启动会自动创建以下表：
- `users` - 用户账户表
- `environments` - 攻防环境表
- `attack_logs` - 攻击日志表
- `defense_logs` - 防御日志表
- `ai_decisions` - AI决策记录表

#### 6. 验证数据库连接

启动后端后，查看日志确认数据库连接成功：
- 如果看到 `Database connected successfully` 表示连接成功
- 如果看到 `Using mock data mode` 表示使用模拟数据模式

### 数据库常见问题

#### Q: MySQL 服务无法启动？
A: 
1. 检查 MySQL 安装路径是否正确
2. 查看错误日志：`C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err`
3. 尝试重新安装或修复

#### Q: 连接数据库失败 "Access denied"？
A: 
1. 确认 `.env` 中的密码与 MySQL 设置的密码一致
2. 尝试在命令行用相同密码登录验证：`mysql -u root -p`
3. 如果密码忘记，可以重置 MySQL root 密码

#### Q: 数据库表没有自动创建？
A: 
1. 确认数据库 `ai_security_range` 已创建
2. 确认用户有创建表的权限
3. 查看后端启动日志中的错误信息

#### Q: 如何切换回无数据库模式？
A: 
在 `.env` 中注释或删除数据库配置，或设置无效的连接信息，系统会自动使用模拟数据模式。

---

## 默认账户

系统启动后会自动创建默认管理员账户：
- 用户名：`admin`
- 密码：`admin123`

---

## 常见问题

### Q: pip 命令找不到？
A: 确保安装 Python 时勾选了 "Add Python to PATH"，或重新安装 Python。

### Q: 前端无法连接后端？
A: 确保后端服务在 http://localhost:5000 运行。

### Q: 数据库连接失败？
A: 检查 MySQL 服务是否运行，确认 .env 配置正确。系统支持无数据库模式。

---

## 快速测试（无需Python后端）

前端已启动，可以直接访问 http://localhost:3000 查看界面。
登录页面使用模拟数据，可以体验前端功能。

---

## 技术支持

如有问题，请查看：
- README.md - 项目说明
- QUICKSTART.md - 快速启动指南