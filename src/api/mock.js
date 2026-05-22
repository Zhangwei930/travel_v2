// 数据层 — api.* 调用真实后端接口；下方常量作为离线兜底（请求失败时回退）
import { request } from './request.js'

export const CITY = '乌鲁木齐'

export const WEATHER = {
  temp: 22,
  cond: '晴',
  icon: '☀️',
  advice: '适合出游',
  wind: '东北风 2 级',
}

export const SCENES = [
  { id: 'family', no: '01', label: '亲子游',  icon: '👨‍👩‍👧', color: '#FF6B35', desc: '轻松不太累' },
  { id: 'couple', no: '02', label: '情侣约会', icon: '💑',    color: '#EC4B85', desc: '拍照·夜游' },
  { id: 'rainy',  no: '03', label: '雨天室内', icon: '☔️',    color: '#5B7CFA', desc: '博物馆·商场' },
  { id: 'budget', no: '04', label: '低预算',   icon: '🪙',    color: '#4FD1C5', desc: '免费·Citywalk' },
  { id: 'fish',   no: '05', label: '钓鱼',     icon: '🎣',    color: '#3E5C3A', desc: '水库·黄金时段' },
  { id: 'photo',  no: '06', label: '拍照打卡', icon: '📸',    color: '#A855F7', desc: '地标·出片' },
  { id: 'night',  no: '07', label: '夜游',     icon: '🌃',    color: '#1F2937', desc: '夜市·灯光' },
  { id: 'walk',   no: '08', label: 'Citywalk', icon: '🚶',    color: '#84CC16', desc: '慢走·人文' },
  { id: 'old',    no: '09', label: '适老',     icon: '👵',    color: '#F4B942', desc: '轻量·无障碍' },
]

export const NEARBY = [
  {
    id: 1, no: 'NO.001', name: '新疆博物馆', cat: '博物馆·室内',
    dist: '1.2km', time: '2-3h', budget: '免费',
    tags: ['亲子', '雨天', '文化'],
    img: 'https://picsum.photos/seed/zn1/400/300',
    reason: '室内不受天气影响，了解新疆历史文化',
  },
  {
    id: 2, no: 'NO.002', name: '红山公园', cat: '公园·登高',
    dist: '2.4km', time: '1-2h', budget: '免费',
    tags: ['Citywalk', '晨练'],
    img: 'https://picsum.photos/seed/zn2/400/300',
    reason: '乌鲁木齐市标，登高俯瞰城市全景',
  },
  {
    id: 3, no: 'NO.003', name: '柴窝堡水库', cat: '水库·钓点',
    dist: '48km', time: '半日', budget: '低预算',
    tags: ['钓鱼', '自然', '自驾'],
    img: 'https://picsum.photos/seed/zn3/400/300',
    reason: '周边知名钓点，鱼种丰富，自驾可达',
  },
  {
    id: 4, no: 'NO.004', name: '水磨沟公园', cat: '公园·清晨',
    dist: '3.8km', time: '2-3h', budget: '免费',
    tags: ['自然', '亲子', '晨练'],
    img: 'https://picsum.photos/seed/zn4/400/300',
    reason: '清晨适合散步，水景宜人，人少',
  },
  {
    id: 5, no: 'NO.005', name: '国际大巴扎', cat: '购物·文化',
    dist: '4.1km', time: '2h', budget: '中等',
    tags: ['美食', '拍照', '购物'],
    img: 'https://picsum.photos/seed/zn5/400/300',
    reason: '西域文化与美食荟萃，拍照出片率高',
  },
]

export const ROUTES = [
  {
    id: 1, no: 'R-01', title: '亲子半日游', tag: '亲子', color: '#FF6B35',
    duration: '半日', budget: '低', poi: 3,
    img: 'https://picsum.photos/seed/zr1/500/300',
    summary: '博物馆+本地餐饮+公园，全程室内/近距，孩子不累',
  },
  {
    id: 2, no: 'R-02', title: '柴窝堡钓鱼一日', tag: '钓鱼', color: '#3E5C3A',
    duration: '一日', budget: '中', poi: 3,
    img: 'https://picsum.photos/seed/zr2/500/300',
    summary: '清晨出发→水库下竿→中午岸边野餐→傍晚返程',
  },
  {
    id: 3, no: 'R-03', title: '情侣夜游线', tag: '情侣', color: '#EC4B85',
    duration: '夜晚', budget: '中', poi: 4,
    img: 'https://picsum.photos/seed/zr3/500/300',
    summary: '红山夜景→大巴扎晚餐→咖啡店',
  },
  {
    id: 4, no: 'R-04', title: '低预算 Citywalk', tag: 'Citywalk', color: '#4FD1C5',
    duration: '一日', budget: '免费', poi: 5,
    img: 'https://picsum.photos/seed/zr4/500/300',
    summary: '公园+老街+二道桥，全程公交可达',
  },
]

export const GEAR_LIST = [
  '钓竿×2', '鱼饵(蚯蚓/玉米)', '折叠椅', '遮阳帽', '防虫液', '保温水壶', '垃圾袋',
]

// 场景对应的路线与 POI（按场景 id 过滤）
export const SCENE_ROUTES = {
  fish:   [ROUTES[1]],
  family: [ROUTES[0]],
  couple: [ROUTES[2]],
  walk:   [ROUTES[3]],
  budget: [ROUTES[3]],
  rainy:  [ROUTES[0]],
  photo:  [ROUTES[2]],
  night:  [ROUTES[2]],
  old:    [ROUTES[0]],
}

export const SCENE_POIS = {
  fish:   [NEARBY[2]],
  family: [NEARBY[0], NEARBY[3]],
  couple: [NEARBY[1], NEARBY[4]],
  walk:   [NEARBY[1], NEARBY[3]],
  budget: [NEARBY[0], NEARBY[1], NEARBY[3]],
  rainy:  [NEARBY[0], NEARBY[4]],
  photo:  [NEARBY[1], NEARBY[4]],
  night:  [NEARBY[4], NEARBY[1]],
  old:    [NEARBY[0], NEARBY[3]],
}

export const PLAN_RESULT = {
  no: 'PLAN-2026-0521',
  title: '柴窝堡钓鱼一日方案',
  summary: '根据天气与水况，今日为本周最佳钓鱼日。清晨出发、黄金时段下竿、傍晚返程。',
  totalBudget: '人均 80-180 元',
  totalTime: '约 9 小时',
  people: '2 人',
  weather: '☀️ 22° 晴',
  stops: [
    {
      idx: 1, name: '柴窝堡水库（南岸）', cat: '水域·钓点', arrive: '07:00',
      stay: '4小时', budget: '入场 0 元',
      reason: '南岸早间日影适宜，水温较低，鲫鱼活跃',
      tip: '风向决定坐向，建议背风。蚊虫多需防虫液',
      transport: '自驾·约90分钟',
    },
    {
      idx: 2, name: '岸边野餐区', cat: '休整', arrive: '11:30',
      stay: '1小时', budget: '30-50 元',
      reason: '风向背阴处搭折叠桌椅，避开正午阳光',
      tip: '垃圾必须带走，严禁明火炊事',
      transport: '步行 200 m',
    },
    {
      idx: 3, name: '达坂城风电场观景', cat: '风景·返程', arrive: '15:00',
      stay: '1小时', budget: '免费',
      reason: '回程顺路，巨型风车阵列拍照震撼',
      tip: '路边停车注意车流；强风时段注意防风',
      transport: '自驾·40分钟',
    },
  ],
  gearList: ['钓竿×2', '鱼饵(蚯蚓/玉米)', '折叠椅', '遮阳帽', '防虫液', '保温水壶', '垃圾袋'],
  backup: '若清晨刮 4 级以上大风，改为水磨沟公园+室内活动。如水位变化无鱼讯，转点至下游小水库。',
  disclaimer: '营业、水位、限钓信息以官方/管理处实时通告为准，本攻略仅供参考。',
  sources: [
    { kind: '地图',     t: '柴窝堡 POI · 路线' },
    { kind: '知识库',   t: '钓鱼模板 R-02 · 已审核' },
    { kind: '天气',     t: '实时气象 API' },
    { kind: 'WebSearch', t: '今日限钓公告' },
  ],
}

// API 函数 — 调用真实后端，失败时回退到上方兜底常量
export const api = {
  getWeather: () => request('/api/weather').catch(() => WEATHER),
  getNearby:  (lat, lng) =>
    request(`/api/poi/list${lat != null && lng != null ? `?lat=${lat}&lng=${lng}` : ''}`).catch(() => NEARBY),
  getRoutes:  () => request('/api/route/recommend').catch(() => ROUTES),
  getScenes:  () => request('/api/scene/list').catch(() => SCENES),
  getSceneRoutes: (sceneId) =>
    request(`/api/route/recommend?scene=${sceneId}`).catch(() => SCENE_ROUTES[sceneId] || ROUTES.slice(0, 2)),
  getScenePois: (sceneId) =>
    request(`/api/poi/list?scene=${sceneId}`).catch(() => SCENE_POIS[sceneId] || NEARBY.slice(0, 4)),
  getPoiDetail: (id) =>
    request(`/api/poi/detail?id=${id}`).catch(() => NEARBY.find(p => p.id === Number(id)) || NEARBY[0]),
  generateTrip: (payload) =>
    request('/api/trip/generate', { method: 'POST', data: payload }).catch(() => PLAN_RESULT),
  ask: (question, city) =>
    request('/api/kb/ask', { method: 'POST', data: { question, city } }),
  sendFeedback: (payload) =>
    request('/api/feedback', { method: 'POST', data: payload }),
}
