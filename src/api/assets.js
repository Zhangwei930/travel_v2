import { BASE_URL } from './request.js'

const KNOWN_POI_IMAGES = [
  { pattern: /成都博物馆|四川博物院|金沙遗址|武侯祠|杜甫草堂|博物馆/, image: '/static/images/poi-museum-a.svg' },
  { pattern: /人民公园|浣花溪|望江楼|青城山|都江堰|公园/, image: '/static/images/poi-park-a.svg' },
  { pattern: /宽窄巷子|锦里|春熙路|太古里|东郊记忆|街区|Citywalk/, image: '/static/images/poi-city-a.svg' },
  { pattern: /兴隆湖|麓湖|湖|河|湿地|钓点|露营/, image: '/static/images/poi-water-a.svg' },
  { pattern: /火锅|小吃|夜市|茶馆|咖啡|餐厅/, image: '/static/images/poi-food-a.svg' },
]

const POI_GROUPS = {
  park: [
    '/static/images/poi-park-a.svg',
    '/static/images/poi-park-b.svg',
    '/static/images/poi-park-c.svg',
  ],
  museum: [
    '/static/images/poi-museum-a.svg',
    '/static/images/poi-museum-b.svg',
  ],
  indoor: [
    '/static/images/poi-indoor-a.svg',
    '/static/images/poi-indoor-b.svg',
    '/static/images/poi-city-a.svg',
  ],
  food: [
    '/static/images/poi-food-a.svg',
    '/static/images/poi-city-a.svg',
  ],
  water: [
    '/static/images/poi-water-a.svg',
    '/static/images/poi-water-b.svg',
    '/static/images/poi-park-b.svg',
  ],
  city: [
    '/static/images/poi-city-a.svg',
    '/static/images/poi-city-b.svg',
    '/static/images/poi-museum-b.svg',
  ],
  default: [
    '/static/images/poi-default-a.svg',
    '/static/images/poi-park-a.svg',
  ],
}

const ROUTE_IMAGES = {
  short: ['/static/images/route-short-a.svg', '/static/images/route-short-b.svg'],
  half: ['/static/images/route-half-a.svg', '/static/images/route-half-b.svg'],
  day: ['/static/images/route-day-a.svg', '/static/images/route-day-b.svg'],
}

// 微信小程序 <image> 不支持 http，统一升级为 https（高德图片 CDN 均支持 https）
function toHttps(url) {
  return typeof url === 'string' && url.startsWith('http://') ? 'https://' + url.slice(7) : url
}

function textOf(item) {
  return [
    item?.name,
    item?.cat,
    item?.category,
    item?.reason,
    ...(item?.tags || []),
  ].filter(Boolean).join(' ')
}

function groupFor(item) {
  const text = textOf(item)
  if (/博物|展馆|美术|科技|文化|纪念/.test(text)) return 'museum'
  if (/巴扎|夜市|商圈|购物|餐|食|小吃|咖啡|茶/.test(text)) return 'food'
  if (/公园|绿地|自然|景区|乐园|亲子/.test(text)) return 'park'
  if (/湖|河|水库|湿地|海|钓|露营/.test(text)) return 'water'
  if (/室内|商场|书店|影院|咖啡|茶/.test(text)) return 'indoor'
  if (/街|商圈|地标|夜景|Citywalk|步行/.test(text)) return 'city'
  return 'default'
}

function imageIndex(item, size) {
  const raw = String(item?.id ?? item?.name ?? '')
  let sum = 0
  for (let i = 0; i < raw.length; i += 1) sum += raw.charCodeAt(i)
  return Math.abs(sum) % size
}

// fallback 为图片加载失败次数（也兼容旧的布尔值）：0=真实照片，1=定位地图，2+=分类插画
export function poiImage(item, fallback = 0) {
  const level = Number(fallback) || 0
  // 后端不同接口字段名不一：列表用 img，首页 feed/助手卡用 image
  const real = toHttps(item?.img || item?.image)
  if (level === 0 && real) return real
  // 照片缺失或首次加载失败 → 定位地图缩略（仍是真实位置）
  if (level <= 1 && item?.lat != null && item?.lng != null && BASE_URL) {
    return `${BASE_URL}/api/poi/map-thumb?lat=${item.lat}&lng=${item.lng}`
  }
  // 地图也失败 → 分类插画兜底
  const text = textOf(item)
  const known = KNOWN_POI_IMAGES.find(entry => entry.pattern.test(text))
  if (known) return known.image
  const images = POI_GROUPS[groupFor(item)] || POI_GROUPS.default
  return images[imageIndex(item, images.length)]
}

export function routeImage(route, forceFallback = false) {
  const real = toHttps(route?.img || route?.cover_image)
  if (!forceFallback && real) return real
  const duration = String(route?.duration || '')
  const images = /一日|全天|一天|day/i.test(duration)
    ? ROUTE_IMAGES.day
    : /半日|半天|3\s*小时|4\s*小时/i.test(duration)
    ? ROUTE_IMAGES.half
    : ROUTE_IMAGES.short
  return images[imageIndex(route, images.length)]
}
