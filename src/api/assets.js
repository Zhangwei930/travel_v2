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
  ],
  museum: [
    '/static/images/poi-museum-a.svg',
    '/static/images/poi-museum-b.svg',
  ],
  indoor: [
    '/static/images/poi-indoor-a.svg',
    '/static/images/poi-city-a.svg',
  ],
  food: [
    '/static/images/poi-food-a.svg',
    '/static/images/poi-city-a.svg',
  ],
  water: [
    '/static/images/poi-water-a.svg',
    '/static/images/poi-park-b.svg',
  ],
  city: [
    '/static/images/poi-city-a.svg',
    '/static/images/poi-museum-b.svg',
  ],
  default: [
    '/static/images/poi-default-a.svg',
    '/static/images/poi-park-a.svg',
  ],
}

const ROUTE_IMAGES = {
  short: '/static/images/route-short-a.svg',
  half: '/static/images/route-half-a.svg',
  day: '/static/images/route-day-a.svg',
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

export function poiImage(item, forceFallback = false) {
  if (!forceFallback && item?.img) return item.img
  // 无照片但有坐标 → 用后端代理的 AMap 静态地图作为缩略图
  if (!forceFallback && item?.lat && item?.lng) {
    const { BASE_URL } = require('./request.js')
    if (BASE_URL) return `${BASE_URL}/api/poi/map-thumb?lat=${item.lat}&lng=${item.lng}`
  }
  const text = textOf(item)
  const known = KNOWN_POI_IMAGES.find(entry => entry.pattern.test(text))
  if (known) return known.image
  const images = POI_GROUPS[groupFor(item)] || POI_GROUPS.default
  return images[imageIndex(item, images.length)]
}

export function routeImage(route, forceFallback = false) {
  if (!forceFallback && (route?.img || route?.cover_image)) return route.img || route.cover_image
  const duration = String(route?.duration || '')
  if (/一日|全天|一天|day/i.test(duration)) return ROUTE_IMAGES.day
  if (/半日|半天|3\s*小时|4\s*小时/i.test(duration)) return ROUTE_IMAGES.half
  return ROUTE_IMAGES.short
}
