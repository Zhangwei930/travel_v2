// 本地持久化工具 — 无需用户系统，数据存设备
// 四类数据：生成方案历史 / 收藏 POI / 足迹地点 / 收藏方案

const KEY_PLANS       = 'zhoumi_plan_history'
const KEY_POIS        = 'zhoumi_saved_pois'
const KEY_VISITED     = 'zhoumi_visited_pois'   // 升级：从 id[] → POI[]
const KEY_SAVED_PLANS = 'zhoumi_saved_plans_fav'
const KEY_PENDING_SCENE = 'zhoumi_pending_scene'
const KEY_COORDS = 'zhoumi_current_coords'
const KEY_HOME_FEED = 'zhoumi_home_feed'
const KEY_ASSISTANT_CONTEXT = 'zhoumi_assistant_context'
const KEY_USER = 'zhoumi_user_profile'
const KEY_FEEDBACK = 'zhoumi_my_feedback'
const KEY_LOGIN_REDIRECT = 'zhoumi_login_redirect'

function get(key) {
  try { return uni.getStorageSync(key) || [] } catch (e) {
    console.warn(`[storage] get ${key} failed`, e)
    return []
  }
}
function set(key, val) {
  try { uni.setStorageSync(key, val) } catch (e) {
    console.warn(`[storage] set ${key} failed`, e)
  }
}

// 方案历史（自动追加，不重复）
export function addPlanHistory(plan) {
  const list = get(KEY_PLANS)
  if (list.some(p => p.no === plan.no)) return
  list.unshift({ no: plan.no, title: plan.title, summary: plan.summary,
    totalTime: plan.totalTime, totalBudget: plan.totalBudget, createdAt: Date.now() })
  set(KEY_PLANS, list.slice(0, 50))
}
export function getPlanHistory() { return get(KEY_PLANS) }
export function removePlanHistory(no) { set(KEY_PLANS, get(KEY_PLANS).filter(p => p.no !== no)) }
export function clearPlanHistory() { set(KEY_PLANS, []) }

// 收藏 POI
export function toggleSavedPoi(poi) {
  const list = get(KEY_POIS)
  const idx  = list.findIndex(p => p.id === poi.id)
  if (idx >= 0) { list.splice(idx, 1) } else { list.unshift(poi) }
  set(KEY_POIS, list)
  return idx < 0  // true = 已收藏
}
export function isSavedPoi(id) { return get(KEY_POIS).some(p => p.id === id) }
export function getSavedPois() { return get(KEY_POIS) }
export function removeSavedPoi(id) { set(KEY_POIS, get(KEY_POIS).filter(p => p.id !== id)) }
export function clearSavedPois() { set(KEY_POIS, []) }

// 足迹（存完整 POI 对象，便于足迹页渲染；按 id 去重）
export function trackVisit(poi) {
  if (!poi || poi.id == null) return
  const list = get(KEY_VISITED)
  if (list.some(p => p.id === poi.id)) return
  list.unshift({
    id: poi.id, no: poi.no, name: poi.name, cat: poi.cat,
    img: poi.img, dist: poi.dist, visitedAt: Date.now(),
  })
  set(KEY_VISITED, list.slice(0, 200))
}
export function getVisitedList()  { return get(KEY_VISITED) }
export function getVisitedCount() { return get(KEY_VISITED).length }
export function removeVisited(id) { set(KEY_VISITED, get(KEY_VISITED).filter(p => p.id !== id)) }
export function clearVisited() { set(KEY_VISITED, []) }

// 收藏方案（心形按钮手动操作，区别于自动追加的历史）
export function toggleSavedPlan(plan) {
  const list = get(KEY_SAVED_PLANS)
  const idx  = list.findIndex(p => p.no === plan.no)
  if (idx >= 0) { list.splice(idx, 1) } else { list.unshift(plan) }
  set(KEY_SAVED_PLANS, list)
  return idx < 0
}
export function isSavedPlan(no) { return get(KEY_SAVED_PLANS).some(p => p.no === no) }
export function getSavedPlans() { return get(KEY_SAVED_PLANS) }

// Profile 汇总
export function getProfileStats() {
  return {
    plans:   get(KEY_PLANS).length,
    saved:   get(KEY_POIS).length,
    visited: get(KEY_VISITED).length,
  }
}

// 用户资料（微信授权头像 + 昵称，本地持久化）
export function getUserProfile() {
  try { return uni.getStorageSync(KEY_USER) || null } catch (_) { return null }
}
export function setUserProfile(p) {
  try { uni.setStorageSync(KEY_USER, p) } catch (_) {}
}
export function clearUserProfile() {
  try { uni.removeStorageSync(KEY_USER) } catch (_) {}
}

export function setPendingLoginRedirect(url) {
  if (!url) return
  try { uni.setStorageSync(KEY_LOGIN_REDIRECT, url) } catch (_) {}
}

export function consumePendingLoginRedirect() {
  try {
    const url = uni.getStorageSync(KEY_LOGIN_REDIRECT)
    if (url) uni.removeStorageSync(KEY_LOGIN_REDIRECT)
    return url || ''
  } catch (_) {
    return ''
  }
}

// 我的反馈（本设备提交记录，仅本地展示；文字提交走 POST /api/feedback，截图仅存本地）
export function addMyFeedback(item) {
  const list = get(KEY_FEEDBACK)
  list.unshift({
    id: Date.now(),
    type: item.type || '',
    content: item.content || '',
    images: Array.isArray(item.images) ? item.images : [],
    created_at: Date.now(),
  })
  set(KEY_FEEDBACK, list.slice(0, 50))
}
export function getMyFeedback() { return get(KEY_FEEDBACK) }

// 清除临时缓存（首页 feed + 助手上下文），不清除用户数据
export function clearTempCache() {
  ;[KEY_HOME_FEED, KEY_ASSISTANT_CONTEXT].forEach(k => {
    try { uni.removeStorageSync(k) } catch (_) {}
  })
}

export function setPendingScene(sceneId) {
  if (!sceneId) return
  try { uni.setStorageSync(KEY_PENDING_SCENE, sceneId) } catch (e) {
    console.warn('[storage] set pending scene failed', e)
  }
}

export function consumePendingScene() {
  try {
    const sceneId = uni.getStorageSync(KEY_PENDING_SCENE)
    if (sceneId) uni.removeStorageSync(KEY_PENDING_SCENE)
    return sceneId || ''
  } catch (e) {
    console.warn('[storage] consume pending scene failed', e)
    return ''
  }
}

export function getCoords() {
  try { return uni.getStorageSync(KEY_COORDS) || null } catch (_) { return null }
}

export function setHomeFeedCache(feed) {
  if (!feed) return
  try { uni.setStorageSync(KEY_HOME_FEED, { ...feed, cachedAt: Date.now() }) } catch (e) {
    console.warn('[storage] set home feed failed', e)
  }
}

export function getHomeFeedCache(maxAgeMs = 5 * 60 * 1000) {
  try {
    const feed = uni.getStorageSync(KEY_HOME_FEED)
    if (!feed || !feed.cachedAt) return null
    if (Date.now() - feed.cachedAt > maxAgeMs) return null
    return feed
  } catch (_) {
    return null
  }
}

export function setAssistantContext(context) {
  if (!context) return
  try { uni.setStorageSync(KEY_ASSISTANT_CONTEXT, { ...context, cachedAt: Date.now() }) } catch (e) {
    console.warn('[storage] set assistant context failed', e)
  }
}

export function getAssistantContext(maxAgeMs = 30 * 60 * 1000) {
  try {
    const context = uni.getStorageSync(KEY_ASSISTANT_CONTEXT)
    if (!context || !context.cachedAt) return null
    if (Date.now() - context.cachedAt > maxAgeMs) return null
    return context
  } catch (_) {
    return null
  }
}
