// 本地持久化工具 — 无需用户系统，数据存设备

const KEY_PLANS      = 'zhoumi_plan_history'
const KEY_POIS       = 'zhoumi_saved_pois'
const KEY_VISITED    = 'zhoumi_visited_pois'   // 存完整 POI 摘要对象
const KEY_FEEDBACKS  = 'zhoumi_feedbacks'
const KEY_CITY       = 'zhoumi_city'
const KEY_PENDING_SCENE = 'zhoumi_pending_scene'

function get(key) {
  try { return uni.getStorageSync(key) || [] } catch (_) { return [] }
}
function set(key, val) {
  try { uni.setStorageSync(key, val) } catch (_) {}
}

// ── 方案历史（存完整方案对象，供结果页直接加载；最多保留 20 份）──────────
export function addPlanHistory(plan) {
  const list = get(KEY_PLANS)
  if (list.some(p => p.no === plan.no)) return
  list.unshift({ ...plan, createdAt: Date.now() })
  set(KEY_PLANS, list.slice(0, 20))
}
export function getPlanHistory() { return get(KEY_PLANS) }
export function removePlanHistory(no) {
  const list = get(KEY_PLANS).filter(p => p.no !== no)
  set(KEY_PLANS, list)
}

// ── 收藏 POI ──────────────────────────────────────────────────────────────
export function toggleSavedPoi(poi) {
  const list = get(KEY_POIS)
  const idx  = list.findIndex(p => p.id === poi.id)
  if (idx >= 0) { list.splice(idx, 1) } else { list.unshift(poi) }
  set(KEY_POIS, list)
  return idx < 0
}
export function isSavedPoi(id) { return get(KEY_POIS).some(p => p.id === id) }
export function getSavedPois() { return get(KEY_POIS) }

// ── 足迹（存 POI 摘要 + 访问时间）────────────────────────────────────────
export function trackVisit(poi) {
  const list = get(KEY_VISITED)
  if (list.some(p => p.id === poi.id)) return
  list.unshift({ id: poi.id, name: poi.name, cat: poi.cat, img: poi.img || '', visitedAt: Date.now() })
  set(KEY_VISITED, list.slice(0, 100))
}
export function getVisited()      { return get(KEY_VISITED) }
export function getVisitedCount() { return get(KEY_VISITED).length }

// ── 收藏方案（心形按钮手动操作）──────────────────────────────────────────
const KEY_SAVED_PLANS = 'zhoumi_saved_plans_fav'
export function toggleSavedPlan(plan) {
  const list = get(KEY_SAVED_PLANS)
  const idx  = list.findIndex(p => p.no === plan.no)
  if (idx >= 0) { list.splice(idx, 1) } else { list.unshift(plan) }
  set(KEY_SAVED_PLANS, list)
  return idx < 0
}
export function isSavedPlan(no) { return get(KEY_SAVED_PLANS).some(p => p.no === no) }
export function getSavedPlans()  { return get(KEY_SAVED_PLANS) }

// ── 反馈历史 ──────────────────────────────────────────────────────────────
export function addFeedback(fb) {
  const list = get(KEY_FEEDBACKS)
  list.unshift({ ...fb, createdAt: Date.now() })
  set(KEY_FEEDBACKS, list.slice(0, 50))
}
export function getFeedbacks() { return get(KEY_FEEDBACKS) }

// ── 城市 ──────────────────────────────────────────────────────────────────
export function getCity() {
  try { return uni.getStorageSync(KEY_CITY) || '乌鲁木齐' } catch (_) { return '乌鲁木齐' }
}
export function setCity(city) {
  try { uni.setStorageSync(KEY_CITY, city) } catch (_) {}
}

// ── Tab 场景切换（switchTab 不支持参数，落地一次性 pending 值）────────────
export function setPendingScene(sceneId) {
  try { uni.setStorageSync(KEY_PENDING_SCENE, sceneId) } catch (_) {}
}
export function consumePendingScene() {
  try {
    const sceneId = uni.getStorageSync(KEY_PENDING_SCENE)
    if (sceneId) uni.removeStorageSync(KEY_PENDING_SCENE)
    return sceneId || ''
  } catch (_) {
    return ''
  }
}

// ── 用户坐标（供 generate/chat 页使用真实位置）────────────────────────────
const KEY_COORDS = 'zhoumi_coords'
export function setCoords(lat, lng) {
  try { uni.setStorageSync(KEY_COORDS, { lat, lng }) } catch (_) {}
}
export function getCoords() {
  try { return uni.getStorageSync(KEY_COORDS) || null } catch (_) { return null }
}

// ── Profile 汇总 ──────────────────────────────────────────────────────────
export function getProfileStats() {
  return {
    plans:    get(KEY_PLANS).length,
    saved:    get(KEY_POIS).length,
    visited:  get(KEY_VISITED).length,
    feedback: get(KEY_FEEDBACKS).length,
  }
}
