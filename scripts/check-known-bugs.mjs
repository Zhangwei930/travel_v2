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
const profilePage = read('src/pages/profile/profile.vue')
const resultPage = read('src/pages/result/result.vue')
const pagesJson = read('src/pages.json')
const apiLayer = read('src/api/mock.js')
const storage = read('src/api/storage.js')
const catalogRouter = read('server/app/routers/catalog.py')
const tripService = read('server/app/services/trip_service.py')
const weatherProvider = read('server/app/services/weather_provider.py')

assert(!/city:\s*CITY\b/.test(indexPage), 'index route generation must not reference undefined CITY')
assert(/if\s*\(\s*!nearby\.value\.length\s*\)\s*return/.test(indexPage), 'refreshNearby must guard empty nearby list')
assert(/setPendingScene\s*\(\s*sceneId\s*\)/.test(indexPage), 'index scene navigation must persist pending scene')
assert(/consumePendingScene/.test(storage), 'storage must expose consumePendingScene for reliable tab scene handoff')
assert(/onShow/.test(scenesPage) && /consumePendingScene/.test(scenesPage), 'scenes page must consume pending scene on show')
assert(/weather_source_label/.test(weatherProvider), 'weather provider must expose a source label')
assert(!/PlanSource\(kind="天气",\s*t="实时气象 API"\)/.test(tripService), 'trip source must not always claim realtime weather')
assert(/onLoad/.test(detailPage), 'poi detail must read route id from onLoad query')
assert(!/let\s+poiId\s*=\s*1/.test(detailPage), 'poi detail must not default to id=1 when route id is missing')
assert(!/getCurrentPages\(\)[\s\S]*match\(/.test(detailPage), 'poi detail must not parse id from fullPath at module init')
assert(/getNearby:\s*\(\s*city\s*,\s*lat\s*,\s*lng\s*\)/.test(apiLayer), 'nearby API must accept current city and location')
assert(/getSceneRoutes:\s*\(\s*sceneId\s*,\s*city\s*\)/.test(apiLayer), 'scene routes API must accept current city')
assert(/getScenePois:\s*\(\s*sceneId\s*,\s*city\s*,\s*lat\s*,\s*lng\s*\)/.test(apiLayer), 'scene POI API must accept city and location')
assert(/getRoutePlan:\s*\(\s*id\s*,\s*city\s*\)/.test(apiLayer), 'route cards must use a fast route plan endpoint')
assert(/api\.getNearby\(city\.value/.test(indexPage), 'home nearby list must pass city to backend')
assert(/api\.getRoutes\(city\.value\)/.test(indexPage), 'home route list must pass city to backend')
assert(/api\.getRoutePlan\(route\.id,\s*city\.value\)/.test(indexPage), 'home route card must not call slow AI generation')
assert(!/function goResult\(route\)[\s\S]*?api\.generateTrip/.test(indexPage), 'home route card must avoid slow generateTrip')
assert(/api\.getSceneRoutes\(id,\s*getCity\(\)\)/.test(scenesPage), 'scene route list must pass city to backend')
assert(/api\.getScenePois\(id,\s*getCity\(\)/.test(scenesPage), 'scene POI list must pass city to backend')
assert(/api\.getRoutePlan\(route\.id,\s*getCity\(\)\)/.test(scenesPage), 'scene route card must use fast route plan endpoint')
assert(!/function goResult\(route\)[\s\S]*?api\.generateTrip/.test(scenesPage), 'scene route card must avoid slow generateTrip')
assert(/getCoords/.test(detailPage) && /api\.getPoiDetail\(poiId\.value,\s*coords\?\.lat,\s*coords\?\.lng\)/.test(detailPage), 'poi detail must pass saved coordinates for distance/navigation context')
assert(/poi\.provider\s*==\s*"amap"/.test(catalogRouter), 'amap POI details must not use seed defaults for time/budget/reason')
assert(/city=city or settings\.default_city/.test(catalogRouter), 'amap cache rows must be stored with current city')
assert(/provider != "amap"\)[\s\S]*_city_matches/.test(catalogRouter), 'curated POI list must filter by requested city')
assert(/@router\.get\("\/route\/plan"/.test(catalogRouter), 'backend must expose fast route plan endpoint')
assert(/def route_plan_from_template/.test(tripService), 'trip service must build route plans without AI generation')
assert(/city_q = q\.filter\(TravelRoute\.city == city\)/.test(tripService), 'AI generation route picking must scope templates to current city')
assert(/scene_match = city_q\.filter\(TravelRoute\.scene == payload\.scene\)\.first\(\)/.test(tripService), 'AI generation scene route picking must stay in current city')
assert(/marginBottom:\s*tabBarHeight/.test(chatPage), 'assistant input bar must sit above custom tab bar')
assert(!/知识库审核/.test(profilePage), 'profile page must not show manual knowledge review entry')
assert(!/goAdmin/.test(profilePage), 'profile page must not route to manual knowledge review')
assert(!/pages\/admin\/admin/.test(pagesJson), 'admin review page must be removed from app routes')
assert(resultPage.indexOf('<!-- 数据源标签 -->') > resultPage.indexOf('<!-- 免责声明 -->'), 'result data-source chips must not sit between overview and itinerary')

console.log('known bug checks passed')
