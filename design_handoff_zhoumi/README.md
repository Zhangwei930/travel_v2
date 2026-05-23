# Handoff: 周密出游 智能本地出游规划系统

## Overview

「周密出游」是一套基于地图 API、本地知识库、AI 工作流的**本地、即时、场景化**出游规划系统。用户告诉系统当下的时间、人群、预算、偏好，AI 帮助生成可执行的出游方案（路线、推荐理由、停留时间、预算、避坑提醒、备用方案）。

**核心定位（与传统旅游攻略 App 的区别）：**
- ❌ 不做远途旅游攻略（携程、马蜂窝那一套）
- ✅ 解决"今天附近去哪玩、周末怎么玩、雨天去哪、几个地点怎么顺路串起来"
- 🔄 用户反馈 → 沉淀本地知识库 → 越用越准

**目标平台：** 微信小程序为主 + H5 适配，后期可扩展到 App。

---

## ⚠️ 关于设计文件的说明

`design_files/` 目录中的 HTML 文件是**设计参考原型**，使用 React + Babel 在浏览器中跑，仅用于展示视觉效果和交互逻辑，**不可直接用于生产环境**。

开发任务是：**在目标技术栈（推荐 UniApp + Vue3 + uView Plus）中，按照本文档和原型文件的视觉效果还原所有页面**，使用项目已有的设计系统和组件库。

## Fidelity：高保真 (High-Fidelity)

所有原型均为像素级高保真设计，包含精确的颜色、字体、间距、圆角、交互状态（hover/active/选中/空状态）、加载动画、页面切换动画、真实的数据结构和内容。开发时应尽可能还原原型的视觉效果。

---

## Design Tokens（设计令牌）

### 颜色

```css
/* 主色调 */
--z-primary:    #0D4F4A;   /* 墨青绿 — 主色：导航栏、Header、主按钮 */
--z-primary-d:  #062E2B;   /* 深墨青 — 渐变结束色 */
--z-accent:     #FF6B35;   /* 暖橙 — 强调色：CTA、序号、数据值 */
--z-amber:      #F4B942;   /* 琥珀 — 提醒色 */
--z-mint:       #4FD1C5;   /* 薄荷 — 辅助绿 */

/* 中性色 */
--z-bg:         #F5F1EB;   /* 暖米白 — 页面背景 */
--z-card:       #FFFFFF;   /* 白色 — 卡片底 */
--z-text:       #1A2E2C;   /* 主文字 */
--z-text-2:     #3B4A40;   /* 次文字 */
--z-muted:      #8B9594;   /* 弱化文字、占位符、章节号 */
--z-border:     #E8E2D8;   /* 边框、分割线 */
--z-line:       #EFEADF;   /* 极浅分割线 */

/* 场景配色（每个场景独立色，仅做标识） */
--scene-family: #FF6B35;   /* 亲子游 */
--scene-couple: #EC4B85;   /* 情侣 */
--scene-rainy:  #5B7CFA;   /* 雨天室内 */
--scene-budget: #4FD1C5;   /* 低预算 */
--scene-fish:   #3E5C3A;   /* 钓鱼 */
--scene-photo:  #A855F7;   /* 拍照 */
--scene-night:  #1F2937;   /* 夜游 */
--scene-walk:   #84CC16;   /* Citywalk */
--scene-old:    #F4B942;   /* 适老 */
```

### 字体

```
主标题：'Noto Serif SC' (思源宋体)，weight 800/900 — 用于页面大标题、章节标题、卡片大标题
正文：'Noto Sans SC' (思源黑体)，weight 400-700 — 用于一般正文
编号：'JetBrains Mono' / 'SF Mono' — 用于 §01、NO.001、R-02、时间戳、数据指标小号字
备用：-apple-system, BlinkMacSystemFont, sans-serif
```

**字号规范：**
```
大标题（serif）：       21-26px / weight 900
中标题（serif）：       14-17px / weight 800
卡片标题（serif）：     12.5-15px / weight 700-800
正文：                  12-14px / weight 400-600
辅助/标注：             10.5-12px / weight 400-500
Mono 编号：             9-10.5px / weight 700 / letter-spacing 0.5-1.5
```

### 圆角

```
页面 Header 圆角：       0（贴边）
内容卡片：               13-14px
小卡片/标签项：          11-12px
按钮：                   11-14px
胶囊标签：               99px（全圆）
列表项内部小元素：       6-9px
图标容器：               10-18px
```

### 阴影

```css
/* 标准卡片 */
box-shadow: 0 1px 6px rgba(13, 79, 74, 0.06);

/* 突出卡片（顶部 AI 输入栏等） */
box-shadow: 0 8px 24px rgba(13, 79, 74, 0.12);

/* 强调按钮（CTA） */
box-shadow: 0 6px 18px rgba(255, 107, 53, 0.44);

/* 主色按钮 */
box-shadow: 0 3px 10px rgba(13, 79, 74, 0.33);
```

### 间距

```
页面左右内边距：    14-16px
卡片内边距：        11-14px
组件间垂直间距：    9-12px
章节间距：          14-18px
```

---

## 视觉语言：「索引风」装饰

这是 V3 的特征 — 在简洁卡片设计基础上，加入轻量的**索引/编号语言**作为装饰细节：

| 元素 | 示例 | 用途 |
|------|------|------|
| §01 / §02 | 章节编号 | 每个 Section 标题前的微弱编号（Mono、灰色） |
| NO.001 | 序列号 | POI 卡片左上角小标签 |
| R-02 | 路线编号 | 路线卡片左上角 |
| PLAN-2026-0521 | 方案编号 | 攻略结果页头部 |
| Q1 / Q2 / Q3 | 问题编号 | 一键生成表单的字段标号 |
| § M1 / § M2 | 菜单组编号 | 个人中心菜单组 |
| Issue NO.05 · LOCAL FIELD GUIDE | 副标 | 首页大标题上方 |

**实现要点：**
- 这些编号用 **JetBrains Mono** 等等宽字体，配灰色 `#8B9594`
- 字号 9-10px，加字距 `letter-spacing: 0.5-1.5px`
- **绝对不要让它们变成主视觉**，只是细节装饰

---

## 底部 Tab Bar

5 个 Tab，中央"一键生成"凸起设计：

| Tab | 标识 | 标签 |
|-----|------|------|
| home | 房子 SVG | 首页 |
| scenes | 4 宫格 SVG | 场景 |
| **generate** | **圆形按钮 + 罗盘箭头 SVG** | **生成（凸起 -14px、52×52、coral 渐变背景）** |
| assistant | 对话气泡 SVG | 助手 |
| profile | 人形 SVG | 我的 |

- **激活状态**：图标和文字变 `#0D4F4A`，未激活 `#8B9594`
- **AI 中央按钮**：`background: linear-gradient(135deg, #FF6B35, #FF9558)`，圆形 52×52，`box-shadow: 0 6px 18px rgba(255,107,53,0.55)`
- 背景：`rgba(255,255,255,0.98)` + `backdrop-filter: blur(20px)`
- 顶部边框：`1px solid #E8E2D8`
- 底部内边距：18px（适配 iOS 安全区）

---

## 页面详情

### 1. 首页 (Home)

**Header**（深墨青渐变 → 米白色，padding: 55px 16px 24px）
- 顶行：📍 城市名 ▼ ＋ 右上角天气胶囊 `☀️ 22° 晴`
- Mono 小标：`ISSUE NO.05 · LOCAL FIELD GUIDE`，10px、灰白色、letter-spacing 1.5
- 大标题：「今天想去哪玩？」serif 24px / weight 900 / letter-spacing 1
- 副标题：天气建议 + 路线数

**AI 输入卡（悬浮 -18px）**
- 白色卡片，圆角 14px，box-shadow: `0 8px 24px rgba(13,79,74,0.12)`
- 左：暖橙圆形图标 34×34（罗盘箭头）
- 中：标题"告诉我你的想法 · AI 帮你规划" + 占位文字
- 右：深墨青小按钮"开始"

**§01 按场景索引（3×3 网格）**
- 9 个场景卡片（含钓鱼），高度 78-82px
- 卡片左上：场景图标 34×34，圆角 10，背景为场景色 18% 透明
- 卡片标题 serif 12.5px
- 描述 10px 灰色
- 右上角 Mono 编号 NO.01-09（fontSize: 9, letter-spacing: 0.5）

**§02 附近现在适合去**
- 副标"基于定位 + 天气 + 时段"
- 右上角"换一批"
- POI 卡片：左图 80×80，右内容
  - 内容左上角 NO.001 Mono 序列号
  - 标题 serif 14.5
  - 类别 10.5px
  - 推荐理由 + 💡 引导符（最多 1 行截断）
  - 底部 3 个 Tag

**§03 精选路线（横滑）**
- 卡片宽 220px，封面 100px
- 封面左上角 R-01 Mono 编号
- 封面底部叠加 serif 标题
- 卡片内：摘要（2行截断）+ 时长/预算/站点 + 场景色 Tag

**底部"越用越准"提示横幅**
- 浅琥珀渐变背景 + 边框
- 🌱 图标 + 标题 + 副标

---

### 2. 场景索引 (Scenes)

**Header**
- §SCENES · INDEX Mono 标
- "按场景索引"大标题
- 9 个场景胶囊横滑切换（含 NO 编号 + 图标 + 名称）

**场景 Hero**
- 场景色背景渐变
- 32px 大图标 + Mono "SCENE · 05" + serif 标题 + 描述

**🎣 钓鱼专属：装备清单卡片**
- 2 列 grid 显示 7 件装备
- 每项左侧 checkbox（场景色边框）
- 底部分割线 + "黄金时段"标注

**§R 推荐路线**
- 全宽卡片，含路线编号、封面渐变、摘要

**§P 推荐地点**
- 2 列 grid（钓鱼场景下单列大卡）
- POI 编号 + 缩略图 + 距离

---

### 3. 一键生成 (Generate)

**填写态：**
- Header：§ GENERATE Mono 标 + "一键生成方案"标题
- 单个白色大卡片包含 5 个问题组（Q1-Q5）：
  - 每组左上：橙色 Q1 编号 + serif 标题 + (hint)
  - Chips 多选/单选样式
- 独立卡片 Q6：自然语言文本框
- 汇总浮条：左侧主色边框 + Mono "※ 我将基于以下条件规划"
- 主 CTA 按钮：50px 高、coral 渐变、serif 文字

**加载态（6 步可视化）：**
- 中央旋转 84px 圆形（罗盘箭头）
- "规划中…"标题 + Mono 进度文字
- 6 步骤列表卡片：
  - 待执行：灰色圆 + 编号 01-06
  - 执行中：橙色脉冲圆
  - 已完成：墨青绿对勾
- 底部渐变进度条

**6 个步骤文案：**
```
01 - 解析你的需求
02 - 地图 API · 查询附近 POI
03 - 知识库检索 · 路线模板匹配
04 - WebSearch · 补充最新信息
05 - 本地 AI · 生成攻略草稿
06 - 质量校验 · 风险检查
```

---

### 4. 攻略结果 (Result)

**Header（深墨青渐变 height: auto）**
- ← 返回 + 心形收藏 + 分享按钮
- Mono 方案编号 PLAN-2026-0521
- 「✨ AI · NEW」橙色徽章（AI 生成时显示）
- serif 大标题 + 摘要
- 4 个数据胶囊：时长/预算/同行/天气

**地图缩略图卡片**
- "🗺 路线总览" + Mono "X STOPS · ~25 MIN"
- SVG 地图：网格 + 路径 + 圆形编号节点

**数据源标签横排**
- 4 个 chip：`[地图] 柴窝堡 POI · 路线`、`[知识库] 钓鱼模板 R-02 · 已审核`、`[天气] 实时气象 API`、`[WebSearch] 今日限钓公告`
- 圆形外圈白卡 + 实心主色编号小标

**§ITN 详细路线（时间线）**
- 左侧 36×36 暖橙圆形编号 01/02/03（serif weight 800）
- 时间线连接线（线性渐变）
- 圆下方 Mono 到达时间
- 右侧卡片：
  - 标题 + 类别·交通方式 + 停留时长
  - 「💡 WHY HERE」墨青绿浅底块
  - 「⚠️ HEADS UP」琥珀色浅底块
  - 底部预算 + "导航 →"

**🔄 备用方案卡片**
**ℹ️ 免责声明虚线框**

**底部 sticky 操作栏：**
- 👍 有用 / 💬 反馈（空心按钮）
- 🧭 开始出发（主色渐变，flex:2）

---

### 5. 地点详情 (POI Detail)

**英雄图区** height: 230px
- 全宽地点图 + 底部渐变遮罩
- 左上角 ← 返回（毛玻璃）
- 右上角 心形收藏

**信息卡（悬浮 -32px）**
- Mono 编号 NO.003
- serif 大标题
- 类别 · 距离
- Tag 行
- 3 列数据：推荐时长 / 预算 / 距离

**§01 推荐理由卡片**
**§02 适合人群与场景（钓鱼场景为"钓况"）**
- 2 列 grid：人群/天气/时段/强度（钓鱼：鱼种/时段/水况/风向）

**§03 ⚠️ 避坑提醒（琥珀色卡片）**
- 4 条列表
- 每条左侧 Mono 编号 01-04

**§04 🗺 搭配路线**
- 钓鱼场景：时间表（自驾·抵达·休整·返程）
- 普通场景：彩色胶囊 + 时段标签流

**底部 sticky：**
- 💬 问助手（边框按钮）
- 🧭 地图导航前往（主色渐变，flex:2）

---

### 6. 出游助手 (Assistant)

**Header**
- 🤖 头像 38×38 + 在线绿点
- serif 标题"出游助手"
- Mono 副标"本地知识库 · 在线"

**消息区**
- AI 消息气泡：白底 + 圆角左下尖、机器人头像 30×30 主色渐变
- 用户消息气泡：墨青绿底白字、圆角右下尖
- AI 消息底部 **数据源徽章**（带 `[知识库] 已审核` Mono 编号）
- 快捷 chips 紧跟 bot 消息（点击发送）
- 打字中：3 个点跳动动画

**底部 FAQ 快捷条**
- 横滑 6 个 FAQ chips（点击直接发送）

**输入区**
- 米白胶囊容器 + 输入框 + 发送圆按钮（输入时主色，空时灰色）

---

### 7. 我的 (Profile)

**Header（深墨青渐变）**
- 头像 62×62 圆形（橙色渐变 + 罗盘🧭）
- Mono "EXPLORER · LV.2"
- serif 昵称"出游探索家"
- 副标"已探索 12 个地方"

**3 列统计卡（悬浮 -32px）**
- 已生成方案 / 已收藏 / 足迹地点
- 大数字用 serif 22px weight 900

**🌱 知识贡献横幅**
- 琥珀色渐变 + 边框
- "已贡献 3 条反馈" + 引导文案 + "查看 ›" 按钮

**§ M1 我的内容**（4 项）
- 每行：Mono 编号 01 + 图标 + 标题 + 副标

**§ M2 设置**（4 项）

**底部署名**
- Mono "地图 API · Dify · 本地 AI · WebSearch"
- serif "※ 周密出游 · 让每一次出游都更稳 ※"

---

## 交互与导航逻辑

```
首页 (Tab)
  ├── 点击 AI 输入卡 / 中央 ⊕ → 一键生成页
  ├── 点击场景宫格 → 场景索引页（自动定位到所选场景）
  ├── 点击附近 POI → 地点详情页
  └── 点击精选路线 → 攻略结果页

场景索引 (Tab)
  ├── 切换顶部场景胶囊（含钓鱼专属装备清单）
  ├── 点击路线 → 攻略结果页
  └── 点击 POI → 地点详情页

一键生成 (Tab)
  ├── 填写 Q1-Q6 → 点击主 CTA
  └── 6 步加载动画（4.5s）→ 自动跳转攻略结果（generated:true）

攻略结果
  ├── 左上角 ← 返回上一页
  ├── 心形 切换收藏
  ├── 点击时间线 POI → 地点详情页
  ├── 👍/💬 反馈触发知识库回流
  └── 🧭 开始出发 → 调起地图

地点详情
  ├── 心形 切换收藏
  ├── 💬 问助手 → 助手页
  └── 🧭 地图导航 → 调起地图

出游助手 (Tab)
  ├── 发送消息 → AI 回答（带数据源徽章）
  └── 点击 FAQ chips / Bot chips → 自动发送

我的 (Tab)
  └── 各菜单项跳转到对应详情页
```

### 页面切换动画

```css
/* 进入新页 push */
animation: zSlideIn 0.28s cubic-bezier(0.25,0.46,0.45,0.94);
@keyframes zSlideIn {
  from { transform: translateX(28px); opacity: 0; }
  to   { transform: translateX(0);    opacity: 1; }
}

/* 返回 pop */
animation: zSlideBack 0.25s cubic-bezier(0.25,0.46,0.45,0.94);

/* Tab 切换 */
animation: zFade 0.2s ease;
```

---

## 状态管理（建议 Pinia）

```js
// global
{
  tab: 'home' | 'scenes' | 'generate' | 'assistant' | 'profile',
  navStack: Array<{ screen, ...params }>,
  location: { city, lat, lng, coords },
  weather: { temp, cond, icon, advice, wind },
  favIds: number[],
  user: { id, nickname, level, contributions, ... },
}

// 各页面局部状态
- 一键生成：step (0-5), form, loading, progress
- 攻略结果：openStop, saved
- 场景索引：activeScene
- 助手：msgs[], input, typing
```

---

## 数据结构

### 城市与天气
```ts
interface City { name: string; coords: string; }
interface Weather { temp: number; cond: string; icon: string; advice: string; wind: string; }
```

### 场景
```ts
interface Scene {
  id: string;       // 'family' | 'couple' | ... | 'fish'
  no: string;       // '01' - '09'
  label: string;
  icon: string;     // emoji
  color: string;    // hex
  desc: string;     // 简短描述
}
```

### POI
```ts
interface POI {
  id: number;
  no: string;        // 'NO.001'
  name: string;
  cat: string;       // 类别
  dist: string;      // 距离 '1.2km'
  time: string;      // 推荐时长
  budget: string;
  tags: string[];
  img: string;
  reason: string;    // AI 推荐理由
}
```

### 路线
```ts
interface Route {
  id: number;
  no: string;       // 'R-02'
  title: string;
  tag: string;      // 场景标签
  color: string;
  duration: string; // '半日' / '一日'
  budget: string;
  poi: number;      // 站点数
  img: string;
  summary: string;
}
```

### 完整攻略
```ts
interface PlanResult {
  no: string;              // 'PLAN-2026-0521'
  title: string;
  summary: string;
  totalBudget: string;
  totalTime: string;
  people: string;
  weather: string;
  stops: Stop[];
  gearList?: string[];     // 钓鱼场景独有
  backup: string;
  disclaimer: string;
  sources: { kind: string; t: string; }[];  // 数据源标签
}

interface Stop {
  idx: number;
  name: string;
  cat: string;
  arrive: string;          // 到达时间
  stay: string;            // 停留时长
  budget: string;
  reason: string;          // WHY HERE
  tip: string;             // HEADS UP
  transport: string;       // 交通方式
}
```

### 助手消息
```ts
interface Message {
  role: 'bot' | 'user';
  text?: string;
  chips?: string[];        // 快捷选项
  sources?: { k: string; v: string; }[];  // 数据源
}
```

---

## API 接口（参考后端方案）

```
POST /api/trip/generate           生成出游攻略
GET  /api/poi/list                附近地点列表
GET  /api/poi/detail?id=xxx       地点详情
GET  /api/route/recommend         推荐路线
POST /api/kb/ask                  助手问答
POST /api/feedback                用户反馈
GET  /api/scenes                  场景列表
```

### 生成攻略请求示例
```json
POST /api/trip/generate
{
  "city": "乌鲁木齐",
  "lat": 43.8256, "lng": 87.6168,
  "time": "周六清晨",
  "people_type": "2人",
  "budget": "200元以内",
  "transport": "自驾",
  "preferences": ["钓鱼", "自然"],
  "custom_text": "希望钓点风小、人少"
}
```

### 返回结构
```json
{
  "no": "PLAN-2026-0521",
  "title": "柴窝堡钓鱼一日方案",
  "summary": "...",
  "totalTime": "约 9 小时",
  "totalBudget": "人均 80-180 元",
  "stops": [...],
  "gearList": [...],
  "backup": "...",
  "disclaimer": "...",
  "sources": [
    { "kind": "地图", "t": "柴窝堡 POI" },
    { "kind": "知识库", "t": "钓鱼模板 R-02" },
    { "kind": "天气", "t": "实时气象 API" },
    { "kind": "WebSearch", "t": "今日限钓公告" }
  ]
}
```

---

## 技术建议

### 推荐技术栈（参考完整方案 PDF）
```
前端：UniApp + Vue3 + Composition API + uView Plus + Pinia
后端：FastAPI 或 Java Spring Boot
工作流：Dify
本地模型：Ollama (qwen2.5:3b/7b)
搜索：SearXNG（自建免费）
内容库：Obsidian（人工策划 + Markdown）
数据库：PostgreSQL + pgvector
缓存：Redis
地图：高德 / 腾讯地图（先接一个）
部署：Oracle Cloud + Nginx + Docker
```

### 目录结构参考
```
pages/
  index/index.vue              # 首页
  scenes/scenes.vue            # 场景索引
  generate/generate.vue        # 一键生成
  generate/loading.vue         # 加载动画
  result/result.vue            # 攻略结果
  poi/detail.vue               # 地点详情
  assistant/chat.vue           # 出游助手
  profile/profile.vue          # 我的

components/
  SectionHeader.vue            # § 编号章节标题
  PoiCard.vue
  RouteCard.vue
  SceneCard.vue
  GearChecklist.vue            # 钓鱼装备清单
  Timeline.vue                 # 攻略时间线
  SourceBadge.vue              # 数据源徽章
  WhyHereBlock.vue
  HeadsUpBlock.vue
  ChatBubble.vue
  MiniMap.vue                  # SVG 路线地图
  BottomTabBar.vue

store/
  user.js
  location.js
  weather.js
  favorites.js

api/
  trip.js   poi.js   route.js   kb.js   feedback.js
```

---

## 关键合规与产品原则

1. **地图数据不入库**：地图 API 仅作实时数据源，POI 名称、坐标可临时缓存并标注 `fetched_at / expires_at`，不要把完整返回 JSON 当作自己的地图数据库永久存储。

2. **AI 不能编造**：营业时间、票价、路线耗时这些**实时数据必须实时调用**，AI 生成的所有内容必须保留**数据源标签**（地图/知识库/WebSearch），并在 UI 上展示。

3. **免责声明必须显示**：营业、水位、限钓等动态信息必须在结果页底部加虚线框免责声明。

4. **知识闭环**：用户每次「👍 有用 / 💬 反馈」都触发 `/api/feedback`，由后台审核后回流到 Obsidian 待审核目录。

5. **小程序限制**：
   - `backdrop-filter` 在低端机降级 → 用纯色 rgba
   - 复杂 SVG 路线图建议用 `<image>` 静态图或 Canvas 实现
   - 表情符号 emoji 在小程序内显示一致，可直接使用

---

## 设计文件

| 文件 | 说明 |
|------|------|
| `design_files/zhoumi.html` | 完整交互原型，浏览器打开 |
| `design_files/zhoumi-screens.jsx` | 所有页面组件源码（含完整数据结构、样式参考、SVG） |
| `design_files/ios-frame.jsx` | iOS 设备框架（仅原型展示用，开发不需要） |

### 如何查看原型
1. 三个文件放在同一文件夹
2. 用浏览器打开 `zhoumi.html`
3. 需要联网加载 Google Fonts 和 React CDN

---

## 注意事项

1. **图片资源**：原型使用 picsum.photos 占位图，正式开发请准备城市自建图库（参考 PDF 第8节图片设计方案）
2. **天气接入**：建议接入高德或彩云天气 API，每小时刷新一次
3. **位置权限**：首次启动需引导用户授权位置，未授权时降级到城市级别推荐
4. **AI 接口**：建议 SSE 流式返回，提升用户感知速度
5. **本地知识库优先**：每次请求先查 Obsidian → 数据库 → 命中率低再触发 WebSearch
6. **钓鱼/夜游/雨天等场景的差异化 UI**：场景详情页根据场景特征显示独有组件（装备清单、黄金时段、室内推荐、夜景模式等）
