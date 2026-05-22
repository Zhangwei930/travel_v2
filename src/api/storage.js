// 本地持久化工具 — 无需用户系统，数据存设备
// 三类数据：生成方案历史 / 收藏 POI / 足迹地点

const KEY_PLANS   = 'zhoumi_plan_history'
const KEY_POIS    = 'zhoumi_saved_pois'
const KEY_VISITED = 'zhoumi_visited_ids'

function get(key) {
  try { return uni.getStorageSync(key) || [] } catch (_) { return [] }
}
function set(key, val) {
  try { uni.setStorageSync(key, val) } catch (_) {}
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

// 足迹（自动追加 id）
export function trackVisit(id) {
  const list = get(KEY_VISITED)
  if (!list.includes(id)) { list.push(id); set(KEY_VISITED, list) }
}
export function getVisitedCount() { return get(KEY_VISITED).length }

// 收藏方案（心形按钮手动操作，区别于自动追加的历史）
const KEY_SAVED_PLANS = 'zhoumi_saved_plans_fav'
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
