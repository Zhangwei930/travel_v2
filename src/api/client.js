// 后端 API 客户端 — 全部走真实接口。
// 调用失败由各页面自行处理（toast / 空状态），不做离线假数据兜底。
import { request } from './request.js'

// 拼 query string，自动跳过 null/undefined/'' 并做 URL 编码
function q(params) {
  const parts = []
  for (const k in params) {
    const v = params[k]
    if (v == null || v === '') continue
    parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
  }
  return parts.length ? '?' + parts.join('&') : ''
}

export const api = {
  // ─── 目录（天气 / 场景 / POI / 路线）─────────────
  getWeather: (city) =>
    request('/api/weather' + q({ city })),
  getHomeFeed: (payload) =>
    request('/api/home/feed' + q(payload || {})),
  getNearbyRecommend: (payload) =>
    request('/api/nearby/recommend' + q(payload || {})),
  getFeaturedRoutes: (payload) =>
    request('/api/routes/featured' + q(payload || {})),
  getScenes: () =>
    request('/api/scene/list'),
  getNearby: (lat, lng, city) =>
    request('/api/poi/list' + q({ lat, lng, city })),
  getScenePois: (sceneId, city, lat, lng) =>
    request('/api/poi/list' + q({ scene: sceneId, city, lat, lng })),
  getPoiDetail: (id, lat, lng) =>
    request('/api/poi/detail' + q({ id, lat, lng })),
  getRoutes: (city, scene) =>
    request('/api/route/recommend' + q({ city, scene })),
  getSceneRoutes: (sceneId, city) =>
    request('/api/route/recommend' + q({ scene: sceneId, city })),
  getGearList: (sceneId) =>
    request('/api/gear/list' + q({ scene: sceneId })),
  getCities: () =>
    request('/api/city/list'),
  geoCity: (lat, lng) =>
    request('/api/geo/city' + q({ lat, lng })),

  // ─── 攻略生成 / 复读 ───────────────────────────
  generateTrip: (payload) =>
    request('/api/trip/generate', { method: 'POST', data: payload }),
  getPlan: (no) =>
    request('/api/trip/plan' + q({ no })),

  // ─── 出游助手 ──────────────────────────────────
  ask: (payload, city, history) => {
    const data = typeof payload === 'string'
      ? { question: payload, city, history: history || [] }
      : (payload || {})
    return request('/api/kb/ask', { method: 'POST', data })
  },

  // ─── 图片视觉识别 ──────────────────────────────
  askVision: (payload) =>
    request('/api/kb/ask_vision', { method: 'POST', data: payload }),

  // ─── 反馈 ──────────────────────────────────────
  sendFeedback: (payload) =>
    request('/api/feedback', { method: 'POST', data: payload }),
  getFeedbackList: () =>
    request('/api/feedback/list'),

  // ─── 系统能力开关 ──────────────────────────────
  getCapability: () =>
    request('/api/capability'),
}
