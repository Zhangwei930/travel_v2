export function setTabBarSelected(selected) {
  // #ifdef MP-WEIXIN
  const pages = getCurrentPages()
  const page = pages[pages.length - 1]
  const tabBar = page?.getTabBar?.()
  if (tabBar) tabBar.setData({ selected })
  // #endif
}

export function setTabBarHidden(hidden) {
  // #ifdef MP-WEIXIN
  const pages = getCurrentPages()
  const page = pages[pages.length - 1]
  const tabBar = page?.getTabBar?.()
  if (tabBar) tabBar.setData({ hidden })
  // #endif
}
