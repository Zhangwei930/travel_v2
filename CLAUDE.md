# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

**周密出游** — 智能本地出游规划系统（微信小程序为主，H5 适配）。
核心定位：解决"今天附近去哪玩、周末怎么玩、雨天去哪"的即时规划，不做远途旅游攻略。

技术栈：UniApp + Vue3 (Composition API) + Pinia + Sass

## 开发命令

```bash
# 安装依赖（需要 --legacy-peer-deps，vite 版本有 peer 冲突）
npm install --legacy-peer-deps

# H5 开发预览 → http://localhost:3000
npm run dev:h5

# 微信小程序开发包（输出到 dist/dev/mp-weixin/，用微信开发者工具打开）
npm run dev:mp-weixin

# H5 生产构建
npm run build:h5

# 微信小程序生产构建
npm run build:mp-weixin
```

## 目录结构

```
src/
  api/mock.js          # 所有 Mock 数据 + api.* 函数（后端接入点）
  uni.scss             # 全局 Design Tokens（颜色/字号/圆角/间距/字族变量）
  App.vue              # 全局样式（工具类 .serif .mono .card .btn-accent 等）
  pages.json           # 路由 + Tab Bar 配置
  manifest.json        # 小程序/H5 平台配置

  pages/
    index/index.vue    # 首页（Tab）
    scenes/scenes.vue  # 场景索引（Tab）
    generate/generate.vue  # 一键生成 + 加载动画（Tab 中央按钮触发）
    result/result.vue  # 攻略结果（非 Tab，navigateTo）
    poi/detail.vue     # 地点详情（非 Tab，navigateTo）
    assistant/chat.vue # 出游助手（Tab）
    profile/profile.vue # 我的（Tab）

  components/
    ZTabBar.vue        # 底部 5-Tab 导航（含中央凸起按钮）
    ZSectionHeader.vue # § N 索引风章节标题
    ZTag.vue           # 场景色胶囊标签

design_handoff_zhoumi/
  README.md            # 完整设计规范（Design Tokens、页面详情、合规原则）
  design_files/
    zhoumi-screens.jsx # 原型组件源码（含完整数据结构和样式参考）
    zhoumi.html        # 可在浏览器直接打开的交互原型
```

## 设计系统规则

所有颜色、间距、字号、字族通过 `src/uni.scss` 中的 Sass 变量引用（前缀 `$z-`），**不要在组件内硬编码颜色值**，场景色除外（场景色在 mock.js 的 SCENES 数据里定义）。

字族三类：
- `$serif`（`font-family: $serif`）— 大标题、卡片标题、数字
- `$mono`（`font-family: $mono`）— §01 编号、NO.001 序号、数据指标，配 `letter-spacing`
- `$sans`（默认）— 正文

索引风装饰（`§ 01`、`NO.001`、`R-02`）用 Mono + `$z-muted` 颜色，字号 `$font-mono`（20rpx），**不能让它们成为主视觉**。

## 路由与导航

- **Tab 页**（首页/场景/助手/我的）用 `uni.switchTab({ url: '/pages/...' })`
- **子页**（生成/结果/详情）用 `uni.navigateTo({ url: '/pages/...' })`
- `switchTab` 不支持传参，Tab 间通信用 `uni.$emit` / `uni.$on`（见首页 → 场景页传递 sceneId 的实现）
- 路由参数在子页通过 `getCurrentPages()` + `$page.fullPath` 解析（见 `result.vue`、`poi/detail.vue`）

## 系统适配规则

每个页面 `onMounted` 里调用 `uni.getSystemInfoSync()` 获取：
- `statusBarHeight` → 用于 Header `paddingTop`（自定义导航栏必需）
- `safeAreaInsets.bottom` → 用于 Tab Bar / 底部操作栏的 `paddingBottom`

`backdrop-filter` 在低端小程序机型不支持，降级使用 `rgba` 纯色背景。

## Mock 数据 → 真实 API 接入

`src/api/mock.js` 中的 `api.*` 函数是统一接入点，全部返回 Promise：

```js
api.getWeather()                  // → Weather
api.getNearby()                   // → POI[]
api.getRoutes()                   // → Route[]
api.getSceneRoutes(sceneId)       // → Route[]
api.getScenePois(sceneId)         // → POI[]
```

接入真实后端时只替换这些函数的实现，页面层不需要改动。

后端接口规范见 `design_handoff_zhoumi/README.md` 的"API 接口"章节。

## 产品合规约束（开发时必须遵守）

1. **结果页必须显示数据源标签**（地图/知识库/WebSearch/天气），UI 已有 `source-chip` 实现。
2. **结果页底部必须有免责声明**（虚线框），UI 已有 `disclaimer` 实现，不能删除。
3. **AI 生成内容不能包含编造的实时数据**（营业时间、票价、路线耗时必须来自实时 API）。
4. **地图 POI 数据不能永久存储**，只能临时缓存并标注过期时间。
5. 用户点击「👍 有用 / 💬 反馈」必须触发 `POST /api/feedback`，回流到知识库审核队列。
