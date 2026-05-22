#!/usr/bin/env bash
# 本地启动脚本：创建虚拟环境、安装依赖、启动服务
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3.12 -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
fi

exec .venv/bin/uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}" --reload
