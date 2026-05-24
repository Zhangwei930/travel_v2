# 周密出游 — 后端服务

智能本地出游规划系统后端，基于 **FastAPI**。对应方案文档《周密出游智能攻略系统_完整方案》。

## 技术栈

- FastAPI + Uvicorn
- SQLAlchemy 2.0（本地 SQLite 零配置 / 生产 PostgreSQL）
- Pydantic v2
- 地图 / AI(Dify·Ollama) / WebSearch(SearXNG) 均为可插拔适配器，默认 stub 实现，无需密钥即可运行

## 快速开始

```bash
cd server
bash run.sh            # 自动建虚拟环境、装依赖、启动
# 服务地址 http://localhost:8000   接口文档 http://localhost:8000/docs
```

手动方式：

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 测试

```bash
cd ..
PYTHONPATH=server python -m unittest discover -s server/tests -p 'test_*.py'
```

首次启动会自动建表并灌入与前端 `src/api/mock.js` 对齐的种子数据（5 个 POI、4 条路线、7 条 FAQ）。

## 接口一览

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/weather` | GET | 实时天气 |
| `/api/scene/list` | GET | 场景列表 |
| `/api/poi/list` | GET | 地点列表（参数 `scene/city/lat/lng/keyword`） |
| `/api/poi/detail` | GET | 地点详情（参数 `id`） |
| `/api/route/recommend` | GET | 路线推荐（参数 `scene/city`） |
| `/api/trip/generate` | POST | 生成出游攻略 |
| `/api/kb/ask` | POST | 出游助手问答 |
| `/api/feedback` | POST | 用户反馈 |
| `/api/admin/kb/pending` | GET | 待审核知识列表（需 `X-Admin-Token`） |
| `/api/admin/kb/approve` | POST | 审核入库（需 `X-Admin-Token`） |

## 配置

复制 `.env.example` 为 `.env` 后修改。关键项：

- `DATABASE_URL` — 默认 SQLite；生产改 `postgresql+psycopg://user:pwd@host:5432/zhoumi`
- `MAP_PROVIDER` / `AMAP_KEY` — 接真实地图
- `DIFY_API_BASE` `DIFY_API_KEY` 或 `AI_PROVIDER=ollama` — 接真实 AI 生成
- `SEARXNG_BASE` — 接联网搜索
- `ADMIN_TOKEN` — 后台审核令牌

未配置外部服务时全部走本地 stub，不会编造实时数据（符合方案合规约束）。

## 生产数据库

```bash
psql -U zhoumi -d zhoumi -f sql/schema_postgres.sql
```

## 目录结构

```
server/
  app/
    main.py            # 入口、CORS、路由注册
    config.py          # 环境配置
    database.py        # 引擎/会话
    models.py          # 9 张核心表 ORM
    schemas.py         # 请求/响应模型（与前端对齐）
    seed.py            # 种子数据
    taxonomy.py        # 场景/标签体系
    routers/           # 接口层
    services/          # 地图/AI/搜索适配器 + 攻略与问答编排
  sql/schema_postgres.sql
  requirements.txt
  run.sh
```
