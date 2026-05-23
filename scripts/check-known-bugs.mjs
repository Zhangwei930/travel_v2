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
const storage = read('src/api/storage.js')
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

console.log('known bug checks passed')
