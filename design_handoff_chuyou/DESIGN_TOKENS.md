# 设计 Token

> 这些值在 UniApp 项目里应该统一定义为 SCSS 变量或 Vue 主题变量，所有组件引用。

## 🎨 颜色 (Colors)

### 主色 — 森林绿系
| Token | Hex | 用途 |
|---|---|---|
| `--c-green` | `#1A8870` | 主色 · 按钮 · 高亮 · 主要图标 |
| `--c-green-d` | `#0F5E4D` | 深绿 · 大标题 · 主CTA按钮背景 |
| `--c-green-l` | `#E8F2EC` | 浅绿底 · 标签底色 · 头部柔和块 |
| `--c-green-ls` | `#F2F7F4` | 极浅绿 · 卡片柔和底 |
| `--c-green-line` | `#D5E8DD` | 绿色边线 · 雷达圈 |

### 中性色
| Token | Hex | 用途 |
|---|---|---|
| `--c-bg` | `#FAFBFA` | 页面背景 |
| `--c-card` | `#FFFFFF` | 卡片背景 |
| `--c-text` | `#1F2A2A` | 正文 · 标题 |
| `--c-text-sub` | `#4B5563` | 次要正文 |
| `--c-muted` | `#9CA3AF` | 占位/辅助文字 |
| `--c-border` | `#EFEFEF` | 分割线 · 卡片边 |

### 强调与状态
| Token | Hex | 用途 |
|---|---|---|
| `--c-star` | `#F5B940` | 评分星标 · 太阳图标 |
| `--c-tag-blue-bg` | `#E5F0FA` | 蓝色标签底 (室内/亲子) |
| `--c-tag-blue` | `#4A90C8` | 蓝色标签文字 |
| `--c-tag-pink-bg` | `#FCE8EC` | 粉色标签底 (情侣/拍照) |
| `--c-tag-pink` | `#C8597A` | 粉色标签文字 |

### 分类卡片专用色
| 类别 | 底色 | 备注 |
|---|---|---|
| 亲子游 / Citywalk / 钓鱼露营 | `#DCEDE0` | 浅绿 |
| 情侣约会 / 拍照打卡 | `#FAE2E7` | 浅粉 |
| 雨天室内 | `#E2EBF7` | 浅蓝 |
| 低预算 | `#FAEED0` | 浅黄 |
| 夜游 | `#E5E2EF` | 浅紫 |
| 适老休闲 | `#F0E8DC` | 米色 |

## 📝 字体 (Typography)

**字体族**：`"PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, sans-serif`

**全局**：
- `font-feature-settings: "palt" 1` (中文字距优化)
- `letter-spacing: 0.01em`
- `-webkit-font-smoothing: antialiased`

### 字号字重层级
| Token | size | weight | 用途 |
|---|---|---|---|
| `display-xl` | 44px / line-height 1.2 | 800 | 启动页主标题「出游助手」 |
| `display-lg` | 32px | 800 | 「正在定位中...」、地点名 |
| `title-xl` | 24px | 800 | 首页绿色标题 |
| `title-lg` | 20px | 800 | 卡片大标题 |
| `title-md` | 17–19px | 700–800 | NavBar 标题、Section 标题 |
| `title-sm` | 15–16px | 700 | 卡片标题 |
| `body` | 14px | 400 | 正文、副标题 |
| `body-sm` | 13px | 400 | 次要正文 |
| `caption` | 11–12px | 400 | 辅助文字、Tab 文字 |

## 📐 间距 (Spacing)

8 点网格：
- `4 / 8 / 12 / 14 / 16 / 18 / 20 / 24 / 28 / 32`
- 页面左右内边距：**18px**
- 卡片内边距：**12-14px**
- 卡片间距：**10-12px**

## 🔘 圆角 (Border Radius)

| Token | px | 用途 |
|---|---|---|
| `r-sm` | 6-8 | 标签 chip、小按钮 |
| `r-md` | 10-12 | 卡片缩略图、输入框 |
| `r-lg` | 14-16 | 卡片、分类块 |
| `r-xl` | 22-30 | 主按钮 (跟着路线导航)、聊天输入框、雷达 |
| `r-pill` | 9999 | 圆形头像、圆形图标按钮 |

## 🌥 阴影 (Shadows)

| Token | 值 | 用途 |
|---|---|---|
| `shadow-card` | `0 1px 3px rgba(0,0,0,0.04)` | 普通卡片 |
| `shadow-card-lg` | `0 2px 6px rgba(0,0,0,0.03)` | 路线卡 |
| `shadow-phone` | — | iPhone 框装饰用，App 内不需要 |

## 📱 屏幕基准

- 设计基准：iPhone 14 (393 × 852, @3x)
- iOS 状态栏占位：44pt
- 底部 Home Indicator：34pt
- 底部 Tab Bar 高度：约 80pt (含底部安全区)

## 🧩 组件原型清单

| 组件 | 用处 |
|---|---|
| `PhoneStatusBar` | 9:41 + 信号/WiFi/电池 |
| `NavBar` | ← 标题 / 副标题 / 右侧 action |
| `TabBar` | 底部 4 tab (出游/发现/咨询/我的) |
| `Chip` | 标签 (green/blue/pink/plain) |
| `PlaceCard` | 地点卡（缩略图+标题+描述+距离+评分） |
| `RouteCard` | 路线卡 |
| `EntryCard` | 首页大入口卡 (2x2 网格) |
| `CategoryCard` | 分类大色块卡 |
| `ChatBubble` | 机器人/用户气泡 |
| `RobotMascot` | 机器人吉祥物 SVG |
