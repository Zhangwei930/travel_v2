-- 周密出游 — PostgreSQL 生产库表结构
-- 对应方案文档第 9 章。本地开发用 SQLite 自动建表即可，生产环境执行本脚本。

CREATE TABLE IF NOT EXISTS poi_index (
    id              SERIAL PRIMARY KEY,
    provider        VARCHAR(20) DEFAULT 'stub',     -- amap / tencent / stub
    provider_poi_id VARCHAR(100),
    name            VARCHAR(200) NOT NULL,
    city            VARCHAR(50),
    address         TEXT,
    lat             NUMERIC(10,6),
    lng             NUMERIC(10,6),
    category        VARCHAR(100),
    source          VARCHAR(50),
    fetched_at      TIMESTAMP,
    expires_at      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS travel_knowledge (
    id               SERIAL PRIMARY KEY,
    poi_id           INTEGER REFERENCES poi_index(id),
    scene_ids        TEXT[],                        -- 过滤用场景 id
    scene_tags       TEXT[],                        -- 展示标签：亲子/雨天/夜游
    suitable_people  TEXT[],
    suitable_weather TEXT[],
    recommend_reason TEXT,
    play_duration    VARCHAR(50),
    budget_level     VARCHAR(50),
    best_time        VARCHAR(100),
    avoid_tips       TEXT,
    route_suggestion TEXT,
    cover_image      TEXT,
    display_no       VARCHAR(20),
    content_source   VARCHAR(50) DEFAULT '人工',     -- 人工/AI/WebSearch/用户反馈
    review_status    VARCHAR(20) DEFAULT 'approved', -- pending/approved/rejected
    updated_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS travel_routes (
    id            SERIAL PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    city          VARCHAR(50),
    scene         VARCHAR(50),
    scene_label   VARCHAR(50),
    duration      VARCHAR(50),
    budget_level  VARCHAR(50),
    poi_ids       INTEGER[],
    route_text    TEXT,
    tips          TEXT,
    cover_image   TEXT,
    display_no    VARCHAR(20),
    color         VARCHAR(20),
    review_status VARCHAR(20) DEFAULT 'approved',
    updated_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS faq_knowledge (
    id            SERIAL PRIMARY KEY,
    question      TEXT NOT NULL,
    answer        TEXT NOT NULL,
    category      VARCHAR(50),
    city          VARCHAR(50),
    keywords      TEXT[],
    review_status VARCHAR(20) DEFAULT 'approved',
    updated_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS search_cache (
    id         SERIAL PRIMARY KEY,
    query      TEXT NOT NULL,
    results    JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kb_pending (
    id               SERIAL PRIMARY KEY,
    question         TEXT,
    generated_answer TEXT,
    source_urls      TEXT[],
    city             VARCHAR(50),
    category         VARCHAR(50),
    risk_level       VARCHAR(20) DEFAULT '低',
    status           VARCHAR(20) DEFAULT 'pending',
    created_at       TIMESTAMP DEFAULT NOW(),
    reviewed_at      TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_requests (
    id         SERIAL PRIMARY KEY,
    city       VARCHAR(50),
    lat        NUMERIC(10,6),
    lng        NUMERIC(10,6),
    params     JSONB,
    result     JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_feedback (
    id          SERIAL PRIMARY KEY,
    target_type VARCHAR(30),
    target_id   VARCHAR(80),
    useful      BOOLEAN,
    rating      INTEGER,
    comment     TEXT,
    handled     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- 向量列建议用 pgvector 扩展；若不启用 pgvector，可用 JSONB 暂存。
-- CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS embedding_chunks (
    id         SERIAL PRIMARY KEY,
    ref_type   VARCHAR(30),
    ref_id     INTEGER,
    content    TEXT,
    embedding  JSONB,          -- 启用 pgvector 后改为 vector(1024)
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_poi_city        ON poi_index(city);
CREATE INDEX IF NOT EXISTS idx_knowledge_poi   ON travel_knowledge(poi_id);
CREATE INDEX IF NOT EXISTS idx_routes_city     ON travel_routes(city);
CREATE INDEX IF NOT EXISTS idx_kb_pending_stat ON kb_pending(status);
