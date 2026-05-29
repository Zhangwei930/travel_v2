# 出游助手 — UI 重设计 · 开发对接包

## 概览

本目录是 [github.com/Zhangwei930/travel_v2](https://github.com/Zhangwei930/travel_v2) 项目的 **UI 重设计交付包**。包含一套全新的、按 12 张参考稿 1:1 设计的高保真原型 (UniApp+Vue3 风格)，以及给 Claude Code CLI 的对接提示词。

## 设计意图

- **风格**：清新森林绿主题，白底/浅卡片为主，吸取了出游、亲子、户外的视觉语言
- **保真度**：**高保真 (Hi-fi)** — 颜色、字号、间距、圆角全部精确，开发者应在 UniApp 中**像素级还原**
- **重要**：本目录内的 HTML/JSX 文件是**设计参考原型**（在浏览器中跑），**不是要直接搬进项目的代码**。开发者应该把这些设计在你现有的 UniApp + Vue3 项目里**重新用 Vue SFC 组件实现**，复用项目已有的请求层、状态管理、路由、后端 API。

## 关键交付原则 ⚠️

> 旧版本的功能比新设计稿多。**新设计稿没出现的旧功能，必须保留**。开发者不要因为设计稿里没画就删掉。

具体策略见 `HANDOFF_PROMPT.md`。

## 目录结构

```
design_handoff_chuyou/
├── README.md               ← 本文件
├── HANDOFF_PROMPT.md       ← 给 Claude Code CLI 的完整对接提示词
├── DESIGN_SPEC.md          ← 12 屏详细设计规范（颜色/字号/间距/组件）
├── DESIGN_TOKENS.md        ← 设计 Token (色板/字体/圆角/阴影)
├── screens/                ← 12 张参考稿原图 (1:1 设计目标)
│   ├── 01-splash.png
│   ├── 02-locating.png
│   ├── ...
│   └── 12-profile.png
└── source/                 ← 高保真 HTML 原型源码（用于本地预览验证）
    ├── 出游助手.html        ← 双击在浏览器打开即可看 12 屏
    ├── chuyou-tokens.jsx
    ├── chuyou-screens-a.jsx
    ├── chuyou-screens-b.jsx
    ├── design-canvas.jsx
    └── assets/
```

## 使用步骤

1. **本地预览**：浏览器打开 `source/出游助手.html`，左右滑动浏览 12 屏，双击任意一屏全屏对比参考稿
2. **打开 Claude Code CLI** 在 travel_v2 项目根目录
3. 把 `HANDOFF_PROMPT.md` 的完整内容复制到 Claude Code 作为第一条消息
4. 把 `screens/` 和 `DESIGN_SPEC.md` 放进 Claude Code 可访问的位置（如项目下 `docs/design/`）
5. 让 Claude Code 按提示词执行重构

## 联系

如果有具体某一屏需要调整或追加变体，在原项目对话中提出即可。
