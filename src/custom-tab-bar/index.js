const TABS = [
  { path: 'pages/index/index',     text: '出游', icon: 'home' },
  { path: 'pages/scenes/scenes',   text: '发现', icon: 'scenes' },
  { path: 'pages/assistant/chat',  text: '咨询', icon: 'chat' },
  { path: 'pages/profile/profile', text: '我的', icon: 'profile' },
]

// 后台开关关闭时不展示「咨询」入口
function visibleTabs() {
  let on = false
  try { on = wx.getStorageSync('zhoumi_consult_on') === true } catch (_) {}
  return on ? TABS : TABS.filter(t => t.path !== 'pages/assistant/chat')
}

function currentSelected(tabs) {
  const pages = getCurrentPages()
  const last = pages[pages.length - 1]
  const route = (last && last.route) || ''
  const idx = tabs.findIndex(t => route === t.path)
  return idx >= 0 ? idx : 0
}

Component({
  data: {
    tabs: [],
    selected: 0,
    hidden: false,
  },
  lifetimes: {
    attached() { this.refresh() },
  },
  pageLifetimes: {
    show() { this.refresh() },
  },
  methods: {
    refresh() {
      const tabs = visibleTabs()
      this.setData({ tabs, selected: currentSelected(tabs) })
    },
    onTap(e) {
      const idx = Number(e.currentTarget.dataset.index)
      const tabs = this.data.tabs
      if (!tabs[idx]) return
      if (idx === this.data.selected) return
      this.setData({ selected: idx })
      wx.switchTab({ url: '/' + tabs[idx].path })
    },
  },
})
