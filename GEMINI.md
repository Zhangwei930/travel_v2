# 周密出游 (Zhoumi Travel) - 智能本地出游规划系统

## Project Overview
「周密出游」是一套基于地图 API、本地知识库、AI 工作流的**本地、即时、场景化**出游规划系统。目标平台以微信小程序为主，兼容 H5。与传统长途旅游攻略不同，本项目专注于解决“今天附近去哪玩”、“周末怎么玩”等本地高频出行需求。

## Technology Stack
- **Framework**: [UniApp](https://uniapp.dcloud.net.cn/) (Vue 3 + Composition API)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Styling**: SCSS / CSS Variables (Design Tokens)
- **Target Platforms**: WeChat Mini Program (`mp-weixin`), H5

## Directory Structure
- `src/`: 主应用源码目录。
  - `pages/`: 应用的所有页面 (例如：`index`, `scenes`, `generate`, `result`, `poi`, `assistant`, `profile`).
  - `components/`: 可复用的 Vue 组件。
  - `store/`: Pinia 状态管理模块。
  - `api/`: API 接口请求定义 (目前包含 `mock.js`).
  - `static/`: 静态资源文件 (如图片、图标)。
  - `custom-tab-bar/`: 自定义底部导航栏组件。
- `design_handoff_zhoumi/`: 设计交接文档及原型文件。包含极为详尽的 UI/UX 规范、颜色变量 (Design Tokens)、交互逻辑等。**开发时需严格遵循此目录下的 `README.md` 指南。**

## Building and Running

本项目基于 Vite 和 UniApp 构建。在安装完依赖 (`npm install`) 后，可以使用以下命令进行开发和打包：

- **H5 端开发**:
  ```bash
  npm run dev:h5
  ```
- **微信小程序端开发**:
  ```bash
  npm run dev:mp-weixin
  ```
  *(注: 运行后需要使用微信开发者工具打开生成的 `dist/dev/mp-weixin` 目录进行预览)*

- **H5 端打包**:
  ```bash
  npm run build:h5
  ```
- **微信小程序端打包**:
  ```bash
  npm run build:mp-weixin
  ```

*(补充说明: 也可以直接使用 HBuilderX 打开本项目进行可视化编译和运行。)*

## Development Conventions & Guidelines

1.  **高保真还原设计 (High-Fidelity)**:
    - 必须严格按照 `design_handoff_zhoumi/README.md` 中定义的设计令牌（Design Tokens：颜色、字号、圆角、阴影等参数）进行样式开发。
    - **特征视觉**：采用轻量的「索引风」装饰 (如 `§01`, `NO.001` 等 JetBrains Mono 等宽字体的灰色角标装饰)，需确保细节还原。
2.  **UI 架构特性**:
    - 所有的页面和路由配置在 `src/pages.json` 中。
    - 使用全局自定义的底部 Tab Bar（注意：中间是一个凸起的"生成"按钮）。
    - 页面全面采用自定义导航栏 (`"navigationStyle": "custom"`)，实现沉浸式视觉体验。
3.  **状态管理 (Pinia)**:
    - 推荐将全局状态（如：当前 Tab、位置信息、天气信息、收藏 ID 列表、用户信息等）提升至 `src/store/` 中集中管理。
    - 每个页面的独立状态 (如表单填写进度、局部 loading 态) 则保留在页面组件内部。
4.  **业务合规与数据原则**:
    - **透明性**：AI 生成的所有结果必须保留并展示**数据源标签**（地图/知识库/WebSearch），严禁凭空捏造营业时间、票价等实时数据。
    - **免责声明**：攻略结果页底部需包含免责声明，特别是针对动态变化的信息（如限流、限钓、水位等）。
    - **数据合规**：地图 API 返回的数据仅供临时缓存使用，严禁将外部地图底层 POI 数据直接持久化入库。
