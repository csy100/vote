# 投票系统后端

## 环境要求
- Python 3.8+
- PostgreSQL

## 安装步骤

1. 创建虚拟环境并激活：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 创建PostgreSQL数据库：
```sql
CREATE DATABASE vote_db;
```

4. 初始化数据库迁移：
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

5. 运行服务器：
```bash
python main.py
```

服务器将在 http://localhost:8000 运行

## API文档

访问 http://localhost:8000/docs 查看完整的API文档

## 主要API端点

- GET /api/poll - 获取当前问卷和投票统计
- POST /api/poll/vote - 提交投票
- WebSocket /ws/poll - 订阅实时投票更新 