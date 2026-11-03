# 医药检测实验室预约系统

面向医药检测机构的检测室预约系统。检测员可以查看检测室和仪器、提交预约，管理员负责审核预约、维护检测室和用户。检验助手可以根据预约规则、安全规范和设备使用规范回答问题，并协助完成预约。

## 功能

- 注册、登录、个人资料、头像和修改密码
- 检测室查询、详情、仪器清单和在线预约
- 我的预约、取消预约；管理员审核通过或驳回
- 管理员维护检测室、仪器和用户，可重置密码
- 首页统计：我的预约、即将开始的预约、检测室数量、待审核数量
- 检验助手：制度问答（检索 `docs/`）和多轮预约

预置检测室：分子检测室、微生物检测室、理化检测室、免疫检测室、样本前处理室（维护中）。

## 技术栈

- 前端：Vue 3、Vite、Element Plus、Pinia、Vue Router、Axios
- 后端：Python 3.13、FastAPI、SQLAlchemy、PyMySQL、JWT
- 数据：MySQL 8
- 助手：LangGraph、LangChain、DeepSeek 兼容接口、Chroma、`BAAI/bge-small-zh-v1.5`

## 目录

```text
docs/          预约规则、安全规范、设备使用规范、管理制度
sql/           建表和初始检测室、仪器数据
server/        FastAPI 后端
web/           Vue 前端
```

以下内容只留在本机，不会提交到 Git：`.env`、`.venv/`、`web/node_modules/`、`chroma_db/`、`uploads/`。

## 环境准备

需要安装 Python 3.13、Node.js、MySQL 8。

创建数据库：

```sql
CREATE DATABASE lab_booking DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

在该库中按顺序执行：

```text
sql/users.sql
sql/labs.sql
sql/equipment.sql
sql/reservations.sql
```

在 `server/` 下新建 `.env`：

```env
DATABASE_URL=mysql+pymysql://用户名:密码@127.0.0.1:3306/lab_booking?charset=utf8mb4
JWT_SECRET=请换成一段随机字符串
LLM_API_KEY=你的模型密钥
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

`LLM_API_KEY` 只在使用检验助手时需要。`.env` 已被忽略，克隆仓库后要自己创建。

## 启动

后端在 `server/` 目录启动：

```powershell
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m scripts.create_test_user
python -m uvicorn app.main:app --reload --port 8000
```

`create_test_user` 会创建管理员 `admin`，初始密码 `123456`。账号已存在时会跳过。

另开一个终端启动前端：

```powershell
cd web
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`。前端会把 `/api` 和 `/static` 代理到 `http://127.0.0.1:8000`。

检测员可以在注册页自行注册。管理员在「用户管理」中新增的账号，初始密码也是 `123456`。

## 检验助手知识库

制度原文在 `docs/`。修改文档后，在 `server/` 目录重建向量库：

```powershell
python -m scripts.build_knowledge
```

脚本会把文档切分后写入项目根目录的 `chroma_db/`。首次运行会下载中文向量模型，需要能访问 Hugging Face 或镜像。重建完成后重启后端，助手才会使用新内容。
