import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

const root = new URL('..', import.meta.url).pathname

function read(path) {
  return readFileSync(join(root, path), 'utf8')
}

function exists(path) {
  return existsSync(join(root, path))
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message)
  }
}

const indexPage = read('src/pages/index/index.vue')
const launchPage = read('src/pages/launch/index.vue')
const locationPage = read('src/pages/location/index.vue')
const scenesPage = read('src/pages/scenes/scenes.vue')
const detailPage = read('src/pages/poi/detail.vue')
const chatPage = read('src/pages/assistant/chat.vue')
const routesPage = read('src/pages/routes/routes.vue')
const routeDetailPage = read('src/pages/routes/detail.vue')
const cityStore = read('src/store/city.js')
const adminPage = read('src/pages/admin/admin.vue')
const resultPage = read('src/pages/result/result.vue')
const pagesJson = read('src/pages.json')
const tabBar = read('src/components/ZTabBar.vue')
const customTabBar = read('src/custom-tab-bar/index.vue')
const apiLayer = read('src/api/mock.js')
const assetLayer = read('src/api/assets.js')
const streamLayer = read('src/api/stream.js')
const storage = read('src/api/storage.js')
const savedPoisPage = read('src/pages/saved/pois.vue')
const savedVisitedPage = read('src/pages/saved/visited.vue')
const profileFootprintPage = read('src/pages/profile/footprint.vue')
const schemas = read('server/app/schemas.py')
const main = read('server/app/main.py')
const homeRouter = read('server/app/routers/home.py')
const catalogRouter = read('server/app/routers/catalog.py')
const kbRouter = read('server/app/routers/kb.py')
const adminRouter = read('server/app/routers/admin.py')
const kbService = read('server/app/services/kb_service.py')
const mapProvider = read('server/app/services/map_provider.py')
const recommendService = read('server/app/services/recommend_service.py')
const kbResolver = read('server/app/services/kb_resolver.py')
const routeBuilder = read('server/app/services/route_builder.py')
const tripService = read('server/app/services/trip_service.py')
const weatherProvider = read('server/app/services/weather_provider.py')
const seedData = read('server/app/seed.py')

assert(!/"pages\/generate\/generate"\s*,\s*"text":\s*"生成"/.test(pagesJson), 'generate page must not remain a primary tab')
assert(/"pages\/scenes\/scenes",\s*"text":\s*"发现"/.test(pagesJson), 'scene tab must be renamed to discover')
assert(/"pages\/assistant\/chat",\s*"text":\s*"咨询"/.test(pagesJson), 'assistant tab must be labeled consult')
assert(/"path":\s*"pages\/routes\/routes"/.test(pagesJson), 'featured routes page must be registered')
assert(!/id:\s*'generate'/.test(tabBar), 'custom tab bar must not show the generate tab')
assert(/label:\s*'发现'/.test(tabBar), 'custom tab bar must show discover label')
assert(/label:\s*'咨询'/.test(tabBar), 'custom tab bar must label assistant tab as consult')

assert(/api\.getHomeFeed/.test(indexPage), 'home page must load the location-first feed')
assert(/onLoad/.test(indexPage) && /onShow/.test(indexPage), 'home page must request location from page lifecycle')
assert(/uni\.getLocation\(\{\s*type:\s*'gcj02'/.test(indexPage), 'home page must request gcj02 location first')
assert(/locationError/.test(indexPage), 'home page must have a location failure gate')
assert(!/开启定位后才能推荐附近真实可去的地点/.test(indexPage), 'home page must not hide all content when location permission is denied')
assert(/DEFAULT_CITY\s*=\s*'成都'/.test(cityStore) && /30\.5728/.test(cityStore) && /104\.0668/.test(cityStore), 'frontend default location must fall back to Chengdu')
assert(/setDefaultLocation/.test(cityStore), 'city store must expose an explicit default-location fallback')
assert(/setDefaultLocation\(\)/.test(launchPage) && !/gotoLocation\(\)/.test(launchPage), 'launch must enter home with default recommendations when location fails')
assert(/setDefaultLocation\(\)/.test(locationPage), 'location page must use the same default-location fallback')
assert(/fallbackLocationUsed/.test(indexPage), 'home page must show default recommendations when location fails')
assert(/entryIcon\(entry\.id\)/.test(indexPage) && /mascot-avatar-text/.test(indexPage), 'home assistant and entry icons must use mini-program-safe text icons')
assert(/@tap\.stop="navPoi\(poi\)"/.test(indexPage), 'home destination cards must expose a dedicated one-tap navigation action')
assert(/function navPoi\(poi\)[\s\S]*?uni\.openLocation/.test(indexPage), 'home destination cards must support one-tap navigation')
assert(/kb_status/.test(indexPage), 'home cards must show knowledge status')
assert(!/function goResult\(route\)[\s\S]*?api\.generateTrip/.test(indexPage), 'home route cards must avoid slow generateTrip')
assert(/出游助手/.test(indexPage), 'home page must be the travel assistant home')
assert(/默认推荐距离/.test(indexPage) && /3-5km/.test(indexPage), 'home page must show default 3-5km radius')
assert(/按场所索引/.test(indexPage) && /附近现在适合去/.test(indexPage) && /精选路线/.test(indexPage) && /直接咨询/.test(indexPage), 'home page must show the four primary entries')
assert(/nearby_now/.test(indexPage) && /\/pages\/nearby\/index/.test(indexPage), 'nearby entry must open the dedicated nearby recommendation page')
assert(/\/pages\/routes\/routes/.test(indexPage), 'featured routes entry must open the routes page')
assert(/setAssistantContext/.test(indexPage), 'home page must pass assistant context before opening chat')
assert(/time_slot/.test(indexPage), 'home page must include time slot in assistant context')

assert(/getHomeFeed:\s*\(payload\)/.test(apiLayer), 'api layer must expose home feed')
assert(/\/api\/home\/bootstrap/.test(apiLayer), 'api layer must call the plan-aligned home bootstrap endpoint')
assert(/getNearbyRecommend:\s*\(payload\)/.test(apiLayer) && /\/api\/nearby\/recommend/.test(apiLayer), 'api layer must expose plan-aligned nearby recommendation endpoint')
assert(/getFeaturedRoutes:\s*\(payload\)/.test(apiLayer) && /\/api\/routes\/featured/.test(apiLayer), 'api layer must expose plan-aligned featured routes endpoint')
assert(/ask:\s*\(payload/.test(apiLayer), 'assistant API must support structured payload mode')
assert(/\/api\/consult\/ask/.test(apiLayer), 'assistant API must call the plan-aligned consult endpoint')
assert(/\/api\/consult\/ask_stream/.test(streamLayer), 'streaming assistant API must call the plan-aligned consult stream endpoint')
assert(!/开发中/.test(indexPage + scenesPage + chatPage), 'primary user flows must not show unfinished development toasts')

assert(/include_router\(home\.router\)/.test(main), 'FastAPI app must register home router')
assert(/include_router\(home\.compat_router\)/.test(main), 'FastAPI app must register plan-aligned home/nearby/routes compatibility router')
assert(/@router\.get\("\/feed",\s*response_model=HomeFeedOut\)/.test(homeRouter), 'home router must expose GET /api/home/feed')
assert(/@router\.get\("\/bootstrap",\s*response_model=HomeFeedOut\)/.test(homeRouter), 'home router must expose GET /api/home/bootstrap')
assert(/@compat_router\.get\("\/nearby\/recommend",\s*response_model=list\[RecommendPoiOut\]\)/.test(homeRouter), 'backend must expose GET /api/nearby/recommend')
assert(/@compat_router\.get\("\/routes\/featured",\s*response_model=list\[RouteCardOut\]\)/.test(homeRouter), 'backend must expose GET /api/routes/featured')
assert(/lat:\s*float\s*=\s*Query\(\.\.\.\)/.test(homeRouter), 'home feed must require latitude')
assert(/lng:\s*float\s*=\s*Query\(\.\.\.\)/.test(homeRouter), 'home feed must require longitude')
assert(/recommend_pois/.test(homeRouter), 'home feed must score destination cards')
assert(/build_home_routes/.test(homeRouter), 'home feed must return route cards')
assert(/scene_index=SCENES/.test(homeRouter), 'home feed must include scene index')

assert(/class RecommendPoiOut/.test(schemas), 'schemas must define recommend POI output')
assert(/class RouteCardOut/.test(schemas), 'schemas must define route card output')
assert(/class HomeFeedOut/.test(schemas), 'schemas must define home feed output')
assert(/lat:\s*float \| None/.test(schemas) && /lng:\s*float \| None/.test(schemas), 'assistant request must accept location context')
assert(/destinations:\s*list\[RecommendPoiOut\]/.test(schemas), 'assistant response must return destination cards')
assert(/routes:\s*list\[RouteCardOut\]/.test(schemas), 'assistant response must return route cards')

assert(/AMAP_TYPES_BY_SCENE/.test(mapProvider), 'map provider must map POI types by scene')
assert(/def amap_types_for_scene/.test(mapProvider), 'map provider must expose scene type lookup')
assert(/def recommend_pois/.test(recommendService), 'recommend service must score and sort POIs')
assert(/resolve_kb_status/.test(recommendService), 'recommend service must include knowledge status in scoring')
assert(/def resolve_kb_status/.test(kbResolver), 'kb resolver must define knowledge status checks')
assert(/hit/.test(kbResolver) && /partial/.test(kbResolver) && /miss/.test(kbResolver) && /stale/.test(kbResolver), 'kb resolver must cover core statuses')
assert(/def build_home_routes/.test(routeBuilder), 'route builder must create home route cards')

assert(/destinations/.test(kbRouter) && /routes/.test(kbRouter), 'streaming assistant metadata must include cards')
assert(/@router\.post\("\/consult\/ask",\s*response_model=AskOut\)/.test(kbRouter), 'backend must expose POST /api/consult/ask')
assert(/@router\.post\("\/consult\/ask_stream"\)/.test(kbRouter), 'backend must expose POST /api/consult/ask_stream')
assert(/@router\.post\("\/kb\/analyze"/.test(adminRouter), 'admin API must expose AI-assisted knowledge review')
assert(/_location_cards/.test(kbService), 'assistant service must build location cards')
assert(/recommend_pois/.test(kbService), 'assistant service must reuse destination recommendation')
assert(/build_home_routes/.test(kbService), 'assistant service must reuse route cards')

assert(!/assistant-menu/.test(chatPage), 'chat page must not render the four-entry home menu')
assert(/onLoad/.test(chatPage) && /getAssistantContext/.test(chatPage), 'chat page must receive context from home')
assert(/lat:\s*chatContext\.value\.lat/.test(chatPage), 'assistant ask payload must include latitude from home context')
assert(/lng:\s*chatContext\.value\.lng/.test(chatPage), 'assistant ask payload must include longitude from home context')
assert(/city:\s*chatContext\.value\.city/.test(chatPage), 'assistant ask payload must include city from home context')

assert(/api\.getHomeFeed/.test(routesPage), 'routes page must load featured routes from the home feed')
assert(/route\.stops/.test(routesPage), 'routes page must render route stops')
assert(/\/pages\/routes\/detail/.test(routesPage), 'routes page must open route detail cards')
assert(/uni\.openLocation/.test(routeDetailPage), 'route detail page must support route navigation')
assert(/chooseNavStop/.test(routeDetailPage) && /showActionSheet/.test(routeDetailPage), 'route detail must let users choose a stop before route navigation')

assert(/onShow/.test(scenesPage), 'scenes page must refresh from tab lifecycle')
assert(/onLoad/.test(detailPage), 'poi detail must read route id from onLoad query')
assert(!/let\s+poiId\s*=\s*1/.test(detailPage), 'poi detail must not default to id=1 when route id is missing')
assert(!/getCurrentPages\(\)[\s\S]*match\(/.test(detailPage), 'poi detail must not parse id from fullPath at module init')
assert(/getNearby:\s*\(\s*lat\s*,\s*lng\s*,\s*city\s*\)/.test(apiLayer), 'nearby API must keep legacy current location parameters')
assert(/provider != "amap"\)[\s\S]*_city_matches/.test(catalogRouter), 'curated POI list must filter by requested city')
assert(/weather_source_label/.test(weatherProvider), 'weather provider must expose a source label')
assert(!/PlanSource\(kind="天气",\s*t="实时气象 API"\)/.test(tripService), 'trip source must not always claim realtime weather')
assert(/from app\.config import settings/.test(recommendService), 'recommend service must import settings before using amap image fallback')
assert(!/picsum\.photos|images\.unsplash\.com/.test(apiLayer + indexPage + routesPage + scenesPage + detailPage + seedData), 'production UI and seed data must not use random remote placeholder photos')
assert(/function groupFor/.test(assetLayer) && /export function poiImage/.test(assetLayer) && /export function routeImage/.test(assetLayer), 'UI must use local deterministic image fallbacks')
assert(/KNOWN_POI_IMAGES/.test(assetLayer), 'known scenic spots must map to matching local images')
assert(/\/static\/images\/poi-park-a\.svg/.test(assetLayer) && /\/static\/images\/route-day-a\.svg/.test(assetLayer), 'fallback assets must be local static images')
for (const image of [
  'poi-park-a.svg',
  'poi-park-b.svg',
  'poi-museum-a.svg',
  'poi-museum-b.svg',
  'poi-indoor-a.svg',
  'poi-city-a.svg',
  'poi-food-a.svg',
  'poi-water-a.svg',
  'poi-default-a.svg',
  'route-short-a.svg',
  'route-half-a.svg',
  'route-day-a.svg',
]) {
  assert(exists(`src/static/images/${image}`), `${image} fallback asset must exist`)
}
assert(/poiThumb\(poi\)/.test(indexPage) && /routeThumb\(route\)/.test(indexPage), 'home cards must render local fallback thumbnails')
assert(/poiThumb\(poi\)/.test(read('src/pages/nearby/index.vue')), 'nearby page must render local fallback thumbnails')
assert(/poiThumb\(poi\)/.test(read('src/pages/scenes/result.vue')), 'scene result page must render local fallback thumbnails')
assert(/routeThumb\(route\)/.test(routesPage), 'routes page must render local fallback thumbnails')
assert(/heroImage/.test(detailPage) && /poiImage\(poi\.value/.test(detailPage), 'poi detail hero must render a local fallback image')
assert(/poiImage/.test(chatPage) && /assistant-poi-thumb/.test(chatPage), 'assistant destination cards must include nonblank thumbnails')
assert(/setStorageSync\('currentPoiPreview'/.test(chatPage) && /currentPoiPreview/.test(detailPage), 'assistant destination detail must reuse the selected destination preview image')
assert(/poiImage/.test(savedPoisPage) && /poiImage/.test(savedVisitedPage), 'saved lists must show nonblank thumbnails')
assert(!/<image\s+v-if=/.test(indexPage + routesPage + detailPage + chatPage + savedPoisPage + savedVisitedPage + profileFootprintPage), 'image cards must not disappear when upstream images are missing')
assert(/getVisitedList/.test(profileFootprintPage) && !/getVisited/.test(profileFootprintPage.replace(/getVisitedList/g, '')), 'legacy footprint page must use the existing visited storage API')
assert(!/<component\s+:is=/.test(customTabBar), 'WeChat custom tab bar must not rely on unresolved dynamic icon components')
assert(/\/api\/admin\/kb\/analyze/.test(adminPage) && /AI分析/.test(adminPage), 'admin knowledge review must provide AI-assisted analysis')
assert(/marginBottom:\s*tabBarHeight/.test(chatPage) || /bottom:\s*tabBarHeight/.test(chatPage), 'assistant input bar must sit above custom tab bar')
assert(resultPage.includes('<!-- 数据源标签 -->') && resultPage.includes('<!-- 免责声明 -->'), 'result page must keep source labels and disclaimer')

console.log('known bug checks passed')
