# AI智能招聘面试管理系统

## 项目简介
基于 FastAPI + Vue3 的全栈招聘面试管理系统，支持 AI 自动解析面试对话生成结构化总结，实现多轮面试流程线上化流转、候选人全生命周期管理和数据可视化。

## 技术栈
| 层级 | 技术 |
|------|------|
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | SQLite（单文件，零配置） |
| 前端 | Vue3 + Element Plus + ECharts |
| AI | 兼容 OpenAI 接口的大模型（支持豆包/通义千问等） |
| 部署 | Docker + Docker Compose |

## 快速启动

### 方式一：Docker 一键部署（推荐）
```bash
# 1. 克隆项目后进入目录
cd hr-agent

# 2. 复制环境变量配置文件
cp .env.example .env
# 编辑 .env 填入大模型 API Key（可选，不配置也可使用模拟数据）

# 3. 启动服务
docker-compose up -d

# 4. 访问 http://localhost:8000
# 默认管理员：admin / admin123
```

### 方式二：本地开发

**后端：**
```bash
cd backend
pip install -r requirements.txt
python run.py
# 后端启动在 http://localhost:8000
```

**前端：**
```bash
cd frontend
npm install
npm run dev
# 前端启动在 http://localhost:3000
# 开发模式下 API 代理到后端 8000 端口
```

## 环境变量说明
| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PORT` | 服务端口 | 8000 |
| `DATABASE_URL` | 数据库连接 | sqlite:///./data/hr_system.db |
| `SECRET_KEY` | JWT 密钥 | （生产环境请修改） |
| `LLM_API_KEY` | 大模型 API Key | （可选） |
| `LLM_API_BASE` | 大模型接口地址 | https://api.openai.com/v1 |
| `LLM_MODEL` | 模型名称 | gpt-4o-mini |
| `DEFAULT_ADMIN_USERNAME` | 默认管理员账号 | admin |
| `DEFAULT_ADMIN_PASSWORD` | 默认管理员密码 | admin123 |

## 核心功能
1. **AI面试解析** — 粘贴面试对话文本，自动生成结构化面试报告
2. **多轮面试流转** — 初面→复面→终面流程化，状态自动更新
3. **候选人管理** — 全生命周期数据存储、检索、筛选
4. **数据可视化** — 招聘总览看板、趋势统计、岗位维度分析
5. **数据导出** — 候选人列表导出 CSV
6. **系统配置** — 大模型 API、Prompt、账号均可在线配置

## 项目结构
```
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── models/        # 数据库模型
│   │   ├── schemas/       # Pydantic 模型
│   │   ├── services/      # 业务逻辑（AI / 认证）
│   │   └── utils/         # 工具函数
│   ├── run.py             # 启动入口
│   └── requirements.txt
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── api/           # API 接口封装
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由
│   │   └── store/         # 状态管理
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 截图预览
（部署后即可查看完整界面）

## License
MIT
