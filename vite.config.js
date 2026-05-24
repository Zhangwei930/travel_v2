// Vite 配置 — H5 dev 通过 proxy 访问后端，避免跨域 + 让 .env 决定 prod 后端
import { defineConfig, loadEnv } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // dev 时让 /api 走代理到真实后端；prod 走 VITE_API_BASE 拼接绝对地址
  const proxyTarget = env.VITE_DEV_PROXY || 'https://tr.magies.top/zhoumi-api'
  // 直接把 API base 作为字面量注入。避免在 src/api/request.js 里碰 import.meta —
  // mp-weixin 输出会把 typeof import.meta 编成 require("url") 的 polyfill，
  // 小程序运行时没有该模块，导致 BASE_URL 兜底为空。
  const apiBase = env.VITE_API_BASE || ''

  return {
    define: {
      __ZHOUMI_API_BASE__: JSON.stringify(apiBase),
    },
    plugins: [uni()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
          // proxyTarget 已包含 /zhoumi-api 前缀，所以保留 /api/xxx 直接拼接 OK
        },
      },
    },
  }
})
