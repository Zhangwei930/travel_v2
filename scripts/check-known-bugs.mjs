import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'

const root = new URL('..', import.meta.url).pathname

function read(path) {
  return readFileSync(join(root, path), 'utf8')
}

function exists(path) {
  return existsSync(join(root, path))
}

function assert(condition, message) {
  if (!condition) throw new Error(message)
}

function walk(dir) {
  const out = []
  for (const name of readdirSync(join(root, dir))) {
    const rel = `${dir}/${name}`
    const abs = join(root, rel)
    if (statSync(abs).isDirectory()) out.push(...walk(rel))
    else out.push(rel)
  }
  return out
}

const cityStore = read('src/store/city.js')
const indexPage = read('src/pages/index/index.vue')
const scenesPage = read('src/pages/scenes/scenes.vue')
const assistantPage = read('src/pages/assistant/chat.vue')
const profilePage = read('src/pages/profile/profile.vue')
const launchPage = read('src/pages/launch/index.vue')
const locationPage = read('src/pages/location/index.vue')
const nearbyPage = read('src/pages/nearby/index.vue')
const sceneResultPage = read('src/pages/scenes/result.vue')
const entryCard = read('src/components/cy/cy-entry-card.vue')
const placeCard = read('src/components/cy/cy-place-card.vue')
const customTabBar = read('src/custom-tab-bar/index.js')
const pagesJson = read('src/pages.json')
const manifest = read('src/manifest.json')
const resultPage = read('src/pages/result/result.vue')
const sourceFiles = walk('src').filter(path => /\.(vue|js|scss|json)$/.test(path))
const sourceText = sourceFiles.map(path => read(path)).join('\n')
const serverAppFiles = exists('server/app')
  ? walk('server/app').filter(path => /\.(py)$/.test(path))
  : []
const serverAppText = serverAppFiles.map(path => read(path)).join('\n')

assert(!/\s+c0-2\s/.test(entryCard), 'entry card SVG must compile without malformed duplicate attributes')
assert(!/:key="tag"/.test(placeCard), 'place card tags must not use tag text as key because AMap can return duplicate labels')
assert(!/api\/mock\.js/.test(sourceText), 'pages and modules must import the API through src/api/index.js, not the legacy mock filename')
assert(!/console\.log\(/.test(sourceText), 'production source must not keep console.log debugging')
assert(!/开发中|敬请期待|TODO|FIXME/.test(sourceText), 'user flows must not expose unfinished/development text')
assert(!/picsum\.photos|images\.unsplash\.com/.test(sourceText), 'UI must not use random remote placeholder photos')
assert(!/<\/?svg[\s>]/.test(sourceText), 'UI source must not use raw SVG tags; use platform-compatible icon components or image assets')
assert(!/[☀️🌧️💡⭐★😀😃😄😁🙂😊😍❤️💕💬📍🎒🏠👤🧭✨📤🗺⏱💰👥🌤⚠️ℹ️👍🤍✈🔄🚩]/u.test(sourceText), 'UI source must not use emoji text icons; use SVG/components instead')
assert(!/src\/api\/mock\.js/.test(serverAppText), 'server app comments/contracts must not point new work at the legacy frontend mock filename')
assert(!/[☀️⛅️☁️🌧❄️☔️👨‍👩‍👧💑🪙🎣📸🌃🚶👵🌤⏰💪]/u.test(serverAppText), 'server API payloads must not expose emoji icon fields to the UI')

assert(/export const DEFAULT_CITY = '成都'/.test(cityStore), 'store must keep Chengdu as an explicit fallback city')
assert(/KEY_LOCATION_SOURCE/.test(cityStore), 'store must persist whether coords came from real location or default fallback')
assert(/source:\s*readSource\(\)/.test(cityStore), 'store must expose the current location source')
assert(/hasRealLocation/.test(cityStore), 'store must provide a real-location guard')
assert(!/uni\.getStorageSync\(KEY_CITY\) \|\| DEFAULT_CITY/.test(cityStore), 'store must not initialize unknown users as Chengdu')

assert(/uni\.getLocation\(\{\s*type:\s*'gcj02'/.test(launchPage), 'launch must request gcj02 location on first open')
assert(/fail:\s*\(\)\s*=>\s*\{\s*gotoLocation\(\)\s*\}/.test(launchPage), 'launch must show the location flow when location fails')
assert(!/setDefaultLocation\(\)/.test(launchPage), 'launch must not silently default to Chengdu')

assert(/locationError/.test(indexPage), 'home must have a visible location failure state')
assert(/function useDefaultFeed\(\)[\s\S]*setDefaultLocation\(\)/.test(indexPage), 'home may use Chengdu only after an explicit default-city action')
assert(!/catch\s*\([^)]*\)\s*\{[\s\S]{0,180}setDefaultLocation\(\)/.test(indexPage), 'home must not default to Chengdu inside the getLocation failure path')
assert(/retryLocation/.test(indexPage), 'home must let users retry real positioning')
assert(/使用默认城市/.test(indexPage), 'home must label the explicit fallback action')
assert(/15公里内推荐/.test(indexPage), 'home header must show the promised 15km recommendation radius')
assert(!/3\s*[~\-～]\s*5\s*km|3\s*[~\-～]\s*5公里/.test(indexPage), 'home header must not show the old 3-5km radius')
assert(/homeFeedCity/.test(indexPage) && /city:\s*homeFeedCity\.value/.test(indexPage), 'home feed must not send stale cached city when real coordinates are available')

assert(/setDefaultLocation\(\)/.test(locationPage), 'location page must keep an explicit default-city entry action')
assert(/uni\.removeStorageSync\(KEY_CITY\)/.test(cityStore), 'real coordinate updates must clear stale cached city names before reverse geocoding')
assert(/scope\.userLocation/.test(manifest) && /requiredPrivateInfos[\s\S]*getLocation/.test(manifest), 'WeChat manifest must declare location permission and getLocation private info')
assert(/ZTabBar/.test(nearbyPage) && /current="home"/.test(nearbyPage), 'nearby list must preserve the bottom tab bar with home active')
assert(/ZTabBar/.test(sceneResultPage) && /current="scenes"/.test(sceneResultPage), 'category list must preserve the bottom tab bar with discovery active')
assert(/const HIKE_RADIUS_OPTIONS = \[150\]/.test(sceneResultPage), 'hike scene must hide 15/30/50km radius options and only show 150km')
assert(/sceneId\.value === 'hike'\s*\?\s*150\s*:\s*cityStore\.radiusKm/.test(sceneResultPage), 'hike scene must default API requests to 150km')
assert(!/\[\.\.\.RADIUS_OPTIONS,\s*150\]/.test(sceneResultPage), 'hike scene must not append 150km to the global radius options')
assert(exists('src/api/tabbar.js'), 'tab pages must share a custom tabbar selected-state sync helper')
const tabbarHelper = read('src/api/tabbar.js')
assert(/export function setTabBarSelected/.test(tabbarHelper), 'tabbar sync helper must export setTabBarSelected')
for (const [name, page, selected] of [
  ['home', indexPage, 0],
  ['scenes', scenesPage, 1],
  ['assistant', assistantPage, 2],
  ['profile', profilePage, 3],
]) {
  assert(page.includes(`setTabBarSelected(${selected})`), `${name} tab page must sync selected tab ${selected} on show`)
}
assert(/this\.setData\(\{\s*selected:\s*idx\s*\}\)/.test(customTabBar), 'custom tabbar must update selected immediately on tap')

for (const page of [
  'pages/launch/index',
  'pages/location/index',
  'pages/index/index',
  'pages/scenes/scenes',
  'pages/scenes/result',
  'pages/nearby/index',
  'pages/routes/routes',
  'pages/routes/detail',
  'pages/poi/detail',
  'pages/assistant/chat',
  'pages/profile/profile',
]) {
  assert(pagesJson.includes(`"path": "${page}"`), `${page} must be registered`)
}

for (const image of [
  'splash-map.png',
  'poi-park-a.svg',
  'poi-city-a.svg',
  'route-short-a.svg',
  'avatar-default.svg',
  'ui/star-line-green.svg',
]) {
  assert(exists(`src/static/images/${image}`), `${image} must exist for the new UI`)
}

assert(resultPage.includes('<!-- 数据源标签 -->') && resultPage.includes('<!-- 免责声明 -->'), 'result page must keep source labels and disclaimer')
assert(/export \{ api \} from '\.\/client\.js'/.test(read('src/api/index.js')), 'api/index.js must be the page-facing API import')
assert(/function poiImage/.test(read('src/api/assets.js')) && /function routeImage/.test(read('src/api/assets.js')), 'image rendering must use deterministic local fallbacks')
assert(!/require\(['"]\.\/request\.js['"]\)/.test(read('src/api/assets.js')), 'image fallback helpers must not use runtime require')

console.log('known bug checks passed')
