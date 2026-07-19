# Care Plan Generator — 最小 MVP

前端表单 → Django 视图 → 同步调用 Claude → 页面直接显示 care plan → 可下载 .txt。

**刻意省略**（后续逐步加上，体验缺点用的）：
- 无任何输入校验
- 无重复检测（warning/error 规则都没做）
- 无数据库 —— 数据存内存字典，**重启即丢**
- 无队列/worker/websocket —— 提交后浏览器一直转圈等 LLM 返回
- 无测试、无分层（视图直接干所有事）

## 运行

```bash
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up --build
```

打开 http://localhost:8000

不用 Docker 的话：

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python manage.py runserver
```

## 文件结构

```
careplan-mvp/
├── Dockerfile / docker-compose.yml / requirements.txt
├── manage.py
├── config/            # Django 项目配置（无数据库、无 admin）
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── careplans/
    ├── views.py       # 表单 + 生成 + 下载，数据存模块级字典 ORDERS
    ├── llm.py         # 调 Claude（claude-opus-4-8，同步非流式）
    └── templates/careplans/
        ├── form.html
        └── result.html
```
