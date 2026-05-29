const TABS = [
  { path: 'pages/index/index',     text: '出游' },
  { path: 'pages/scenes/scenes',   text: '发现' },
  { path: 'pages/assistant/chat',  text: '咨询' },
  { path: 'pages/profile/profile', text: '我的' },
]

function currentSelected() {
  const pages = getCurrentPages()
  const route = pages[pages.length - 1]?.route || ''
  const idx = TABS.findIndex(t => route === t.path)
  return idx >= 0 ? idx : 0
}

Component({
  data: {
    tabs: TABS,
    selected: 0,
  },
  lifetimes: {
    attached() {
      this.setData({ selected: currentSelected() })
    },
  },
  pageLifetimes: {
    show() {
      this.setData({ selected: currentSelected() })
    },
  },
  methods: {
    onTap(e) {
      const idx = Number(e.currentTarget.dataset.index)
      if (!TABS[idx]) return
      if (idx === this.data.selected) return
      this.setData({ selected: idx })
      wx.switchTab({ url: '/' + TABS[idx].path })
    },
  },
})
