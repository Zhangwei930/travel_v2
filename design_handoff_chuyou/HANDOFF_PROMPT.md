# Claude Code CLI 对接提示词

> **使用方法**：在你的项目 (`travel_v2`) 根目录下打开 Claude Code CLI，把下方 `===PROMPT START===` 到 `===PROMPT END===` 之间的全部内容作为第一条消息发送给 Claude。先确保本 `design_handoff_chuyou/` 文件夹已经拷贝到项目根目录或 `docs/` 下。

---

```
===PROMPT START===

你是我的全栈开发助手。我现在有一个 UniApp + Vue3 的旅游攻略 App 项目（仓库：travel_v2），后端是 Spring Boot + MySQL + Redis + AI 大模型，已经能跑。

我现在要你帮我做一次 **UI 大改版**，把现有的前端 UI **完整替换**成全新的「出游助手」设计稿，但 **绝对不能丢掉旧版本已有但新设计稿里没画的功能**。

================================
🎯 任务目标
================================

1. 把 12 屏全新 UI 在现有 UniApp 项目中**1:1 重新实现**，使用项目已有的技术栈（uni-app + Vue3 + SFC + uni-ui / 自定义组件）。
2. 接入现有的后端 API、状态管理（pinia/vuex）、路由（pages.json），不改后端，不重写网络层。
3. **保留全部旧功能**，包括 AI 攻略生成、攻略详情、城市详情、收藏列表、登录、个人中心等，即便新设计稿里没有这些屏幕——把它们以"二级页面"挂在新 UI 的合适入口下（具体策略见下方"功能映射"）。

================================
📦 设计交付物在哪
================================

所有设计资料都在 `design_handoff_chuyou/` 目录下：
- `screens/01-splash.png` ~ `screens/12-profile.png`：**12 张参考稿**（高保真目标，开发以此为准）
- `DESIGN_SPEC.md`：每一屏的详细布局、字号、颜色、组件说明
- `DESIGN_TOKENS.md`：设计 Token（颜色变量、字体、圆角、阴影、间距）
- `source/出游助手.html`：可在浏览器双击打开的高保真原型（参考交互、动效、像素布局）
- `source/chuyou-tokens.jsx` / `chuyou-screens-a.jsx` / `chuyou-screens-b.jsx`：原型 React 源码（**只看，不抄**——抄设计值而不是抄代码结构）
- `source/assets/splash-cropped.png`：启动屏插画

**重要**：HTML/JSX 是设计参考，不是要搬进项目的代码。请在 UniApp 里用 Vue SFC 重新实现。

================================
🧭 实现步骤（请按顺序执行，每完成一步停下来等我确认）
================================

**Step 1 — 调研现状**
- 读 `package.json`、`pages.json`、`main.js`、`App.vue`、`uni.scss` 或主题文件
- 列出当前 App 的全部页面、路由、tabBar 配置、Pinia/Vuex store、API 模块
- 列出当前 UI 用了什么组件库（uni-ui? uView? 自定义？）
- **产出**：一张「旧 → 新」功能映射表，标明每个旧页面要被新版的哪一屏取代、或挂在哪个入口下

**Step 2 — 建立新设计 Token**
- 在 `uni.scss` (或新建 `styles/theme.scss`) 写入 `DESIGN_TOKENS.md` 里所有色值、字号、圆角、间距变量
- 全局字体改成 `PingFang SC, HarmonyOS Sans SC, Noto Sans SC, system-ui`
- 全局 `font-feature-settings: "palt" 1; letter-spacing: 0.01em; -webkit-font-smoothing: antialiased;`
- 暗黑模式不做（设计稿是浅色）

**Step 3 — 基础组件库**
- 在 `components/cy/` 下建一套**复用组件**，按 `DESIGN_TOKENS.md` 末尾的组件清单：
  - `cy-nav-bar.vue`（自定义导航栏，因为 uni-app 默认的导航栏无法做白底深色返回箭头 + 中标 + 右 action 的细节）
  - `cy-tab-bar.vue`（自定义底部 tabBar — `pages.json` 用 `custom-tab-bar` 或 `custom: true`）
  - `cy-chip.vue`（4 色：green/blue/pink/plain）
  - `cy-place-card.vue`（地点卡，列表/横滑两种排版）
  - `cy-route-card.vue`
  - `cy-entry-card.vue`（首页 2×2 入口大卡）
  - `cy-category-card.vue`（9 色方块）
  - `cy-chat-bubble.vue`
  - `cy-robot-mascot.vue`（机器人 SVG 直接用 source/chuyou-tokens.jsx 里的 svg 内联）
- 每个组件做好 props 类型、emit、slot；不要写死数据

**Step 4 — 重做底部 TabBar（4 tab）**
- 出游 / 发现 / 咨询 / 我的
- 自定义 SVG icon（active 绿、inactive 灰），不用文字 emoji
- pages.json 关闭原生 tabBar，用 `custom-tab-bar` 自绘
- 默认进入「出游」tab

**Step 5 — 按屏实现，每屏单独提交 commit**
顺序：03 首页 → 04 分类 → 05 类别列表 → 06 附近 → 07 路线 → 08 路线详情 → 09 地点详情 → 10 咨询开场 → 11 咨询回复 → 12 我的 → 02 定位 → 01 启动
（先做核心 tab 页，再做二级页，再做启动/定位）

每一屏：
1. 看 `screens/<N>-*.png` 参考图
2. 看 `DESIGN_SPEC.md` 对应章节的字号/颜色/间距说明
3. 用 Vue SFC 重写，复用 Step 3 的组件
4. 接现有后端 API（如果旧版没有对应 API，先用 mock 数据 + 注释 `// TODO: 接 API`）
5. 跑 H5 / 微信小程序两端预览，对照参考图人工 diff

**Step 6 — 旧功能挂载**
按下方"功能映射"把旧版多出来的功能挂进来，不能丢

**Step 7 — 收尾**
- 路由跳转全部联通（顶部返回箭头、卡片点击进详情）
- 跑 build：`npm run build:h5`、`npm run build:mp-weixin`
- 列出已知 issue 让我 review

================================
🔁 功能映射（旧 → 新）⚠️ 重要
================================

旧版有但新设计稿没出现的功能，**全部保留**，挂法如下：

| 旧功能 | 新挂载位置 |
|---|---|
| AI 攻略生成（输入目的地/天数/预算/偏好） | 「咨询」tab 里加一个 "AI 生成攻略" 大按钮 + 流程页（沿用旧版表单步骤页 UI 即可，可加新设计 token 包装） |
| 多日攻略详情（每日行程/景点/美食/住宿/交通/Tips） | 新的"路线详情"页 (屏 08) 是单日 ≤3 站点。多日详情独立保留，从「我的 → 我的路线/我的攻略」进入 |
| 城市详情（介绍/天气/最佳季节/景点/美食） | 保留独立路由 `/pages/city/detail`，从首页"附近现在适合去"→任一城市标签 → 城市详情 |
| 收藏列表 | 「我的 → 我的收藏」(屏 12 已有此入口) |
| 浏览历史 | 「我的 → 浏览历史」(屏 12 已有此入口) |
| 离线地图 | 「我的 → 离线地图」(屏 12 已有此入口) |
| 登录/注册 | 「我的」顶部「点击登录/注册」点击进 |
| 意见反馈、设置、用户协议、隐私政策 | 「我的 → 设置」内的二级菜单 |
| 分享攻略海报 | 路线详情/地点详情右上角分享按钮 |
| 攻略重新生成 / 编辑 | 我的路线列表项右滑操作或详情页底部 |

如果你在 Step 1 调研里发现还有上表没列出的旧功能，**先列出来问我**，由我决定挂哪里。**严禁删除**任何旧业务逻辑。

================================
💡 实现细节注意
================================

1. **字体**：所有页面顶层容器加 `class="cy-typo"`，全局 css `.cy-typo, .cy-typo * { font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif; }`
2. **颜色**：所有颜色必须从 Token 引用，禁止 inline hex；颜色 Token 命名见 `DESIGN_TOKENS.md`
3. **状态栏**：UniApp 自带 statusBar，不要自己画 9:41。把内容从 statusBar 高度下方开始排
4. **导航栏**：H5 用自定义 nav-bar；小程序用 `"navigationStyle":"custom"` + 自定义；都用 `cy-nav-bar` 组件
5. **图片**：参考稿里的实拍图（公园/动物园等）开发时用 placeholder（如 `https://images.unsplash.com/...` 或后端返回），不要把参考稿当真图嵌进去
6. **机器人吉祥物**：抠 SVG 内联，**不要**把 png 截图当 asset
7. **底部安全区**：所有底部固定栏（TabBar、CTA 按钮）都要 `padding-bottom: env(safe-area-inset-bottom)`
8. **横滑列表**：精选路线/分类筛选用 `scroll-view scroll-x` + `enable-flex`
9. **暗色 / 国际化**：本版不做，保持中文+浅色
10. **性能**：列表用 `vue-virtual-scroller`，长列表分页

================================
✅ 验收标准
================================

- 12 屏每一屏在 H5 + 微信小程序 两端能跑
- 视觉与 `screens/*.png` 参考图人工 diff，差异 ≤ 5%（字号/颜色/间距，机器人吉祥物形状要对）
- 全部旧功能可达（按"功能映射"表 100% 覆盖）
- 路由跳转无断链，返回箭头能回上一页
- 所有颜色/字体走 Token，没有散落 hex
- console 无报错

================================
开始执行 Step 1：调研现状，列出现有页面/路由/store/组件库，输出"旧 → 新"映射表草稿。等我确认后再继续 Step 2。

===PROMPT END===
```

---

## 给本设计稿作者的备注

- 上面的提示词假设用户对 Claude Code 比较熟悉。如果 Claude Code 卡住，可以让他追加：「这一步遇到了什么具体阻力？把你看到的代码片段贴出来，我们一起决定下一步」
- 第一次调研时让 Claude Code 输出"旧 → 新映射表"非常关键——这一步如果跳过，新 UI 上线就可能丢功能
- 如果项目用的是别的目录结构（如 `src/views/` 而非 `pages/`），让 Claude Code 自适应即可
