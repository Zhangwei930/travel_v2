import { readFileSync } from 'node:fs'
import { join } from 'node:path'

const root = new URL('..', import.meta.url).pathname

function read(path) {
  return readFileSync(join(root, path), 'utf8')
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message)
  }
}

const indexPage = read('src/pages/index/index.vue')
const scenesPage = read('src/pages/scenes/scenes.vue')
const detailPage = read('src/pages/poi/detail.vue')
const chatPage = read('src/pages/assistant/chat.vue')
const routesPage = read('src/pages/routes/routes.vue')
const resultPage = read('src/pages/result/result.vue')
const pagesJson = read('src/pages.json')
const tabBar = read('src/components/ZTabBar.vue')
const apiLayer = read('src/api/mock.js')
const storage = read('src/api/storage.js')
const schemas = read('server/app/schemas.py')
const main = read('server/app/main.py')
const homeRouter = read('server/app/routers/home.py')
const catalogRouter = read('server/app/routers/catalog.py')
const kbRouter = read('server/app/routers/kb.py')
const kbService = read('server/app/services/kb_service.py')
const mapProvider = read('server/app/services/map_provider.py')
const recommendService = read('server/app/services/recommend_service.py')
const kbResolver = read('server/app/services/kb_resolver.py')
const routeBuilder = read('server/app/services/route_builder.py')
const tripService = read('server/app/services/trip_service.py')
const weatherProvider = read('server/app/services/weather_provider.py')

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
assert(/nearby\.value\s*=\s*\[\]/.test(indexPage), 'home page must clear nearby recommendations when location fails')
assert(/uni\.openLocation/.test(indexPage), 'home destination cards must support one-tap navigation')
assert(/kb_status/.test(indexPage), 'home cards must show knowledge status')
assert(!/function goResult\(route\)[\s\S]*?api\.generateTrip/.test(indexPage), 'home route cards must avoid slow generateTrip')
assert(/出游助手/.test(indexPage), 'home page must be the travel assistant home')
assert(/默认推荐距离/.test(indexPage) && /3-5km/.test(indexPage), 'home page must show default 3-5km radius')
assert(/按场所索引/.test(indexPage) && /附近现在适合去/.test(indexPage) && /精选路线/.test(indexPage) && /直接咨询/.test(indexPage), 'home page must show the four primary entries')
assert(/scroll-into-view/.test(indexPage) && /nearby_now/.test(indexPage), 'nearby entry must scroll to nearby section')
assert(/\/pages\/routes\/routes/.test(indexPage), 'featured routes entry must open the routes page')
assert(/setAssistantContext/.test(indexPage), 'home page must pass assistant context before opening chat')
assert(/time_slot/.test(indexPage), 'home page must include time slot in assistant context')

assert(/getHomeFeed:\s*\(payload\)/.test(apiLayer), 'api layer must expose home feed')
assert(/\/api\/home\/feed/.test(apiLayer), 'api layer must call the home feed endpoint')
assert(/ask:\s*\(payload/.test(apiLayer), 'assistant API must support structured payload mode')

assert(/include_router\(home\.router\)/.test(main), 'FastAPI app must register home router')
assert(/@router\.get\("\/feed",\s*response_model=HomeFeedOut\)/.test(homeRouter), 'home router must expose GET /api/home/feed')
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
assert(/uni\.openLocation/.test(routesPage), 'routes page must support route navigation')

assert(/onShow/.test(scenesPage), 'scenes page must refresh from tab lifecycle')
assert(/onLoad/.test(detailPage), 'poi detail must read route id from onLoad query')
assert(!/let\s+poiId\s*=\s*1/.test(detailPage), 'poi detail must not default to id=1 when route id is missing')
assert(!/getCurrentPages\(\)[\s\S]*match\(/.test(detailPage), 'poi detail must not parse id from fullPath at module init')
assert(/getNearby:\s*\(\s*lat\s*,\s*lng\s*,\s*city\s*\)/.test(apiLayer), 'nearby API must keep legacy current location parameters')
assert(/provider != "amap"\)[\s\S]*_city_matches/.test(catalogRouter), 'curated POI list must filter by requested city')
assert(/weather_source_label/.test(weatherProvider), 'weather provider must expose a source label')
assert(!/PlanSource\(kind="天气",\s*t="实时气象 API"\)/.test(tripService), 'trip source must not always claim realtime weather')
assert(/marginBottom:\s*tabBarHeight/.test(chatPage) || /bottom:\s*tabBarHeight/.test(chatPage), 'assistant input bar must sit above custom tab bar')
assert(resultPage.includes('<!-- 数据源标签 -->') && resultPage.includes('<!-- 免责声明 -->'), 'result page must keep source labels and disclaimer')

console.log('known bug checks passed')
