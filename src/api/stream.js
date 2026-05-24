// 跨平台流式 POST 调用 — NDJSON 协议
// H5 走 fetch + ReadableStream；mp-weixin 走 uni.request enableChunked + onChunkReceived
//
// 用法:
//   streamAsk({ question, city }, {
//     onMeta:  (m) => { ... },     // 一次，含 sources/chips/hit
//     onChunk: (text) => { ... },  // 多次，AI 流式文本片段
//     onText:  (text) => { ... },  // 一次，命中知识库/缓存时给整段答案
//     onDone:  () => { ... },
//     onError: (err) => { ... },
//   })
import { BASE_URL } from './request.js'

const URL_PATH = '/api/consult/ask_stream'

function dispatchLine(line, handlers) {
  if (!line) return
  let obj
  try { obj = JSON.parse(line) } catch (_) { return }
  switch (obj.event) {
    case 'meta':  handlers.onMeta?.(obj); break
    case 'chunk': handlers.onChunk?.(obj.text || ''); break
    case 'text':  handlers.onText?.(obj.text || ''); break
    case 'done':  handlers.onDone?.(); break
    case 'error': handlers.onError?.(new Error(obj.message || 'stream error')); break
    default: break
  }
}

// ─────────── 共用：按 \n 切片 buffer ───────────
function makeBufferDispatcher(handlers) {
  let buf = ''
  return {
    push(text) {
      buf += text
      let idx
      while ((idx = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, idx).trim()
        buf = buf.slice(idx + 1)
        if (line) dispatchLine(line, handlers)
      }
    },
    flush() {
      const tail = buf.trim()
      if (tail) dispatchLine(tail, handlers)
      buf = ''
    },
  }
}

// #ifdef H5
async function streamAsk_H5(body, handlers) {
  const dispatcher = makeBufferDispatcher(handlers)
  try {
    const resp = await fetch(BASE_URL + URL_PATH, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!resp.ok || !resp.body) {
      handlers.onError?.(new Error('HTTP ' + resp.status))
      return
    }
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      dispatcher.push(decoder.decode(value, { stream: true }))
    }
    dispatcher.flush()
  } catch (e) {
    handlers.onError?.(e)
  }
}
// #endif

// #ifdef MP-WEIXIN
function streamAsk_MP(body, handlers) {
  const dispatcher = makeBufferDispatcher(handlers)
  const decoder = (typeof TextDecoder !== 'undefined') ? new TextDecoder() : null

  function decodeChunk(arrayBuffer) {
    if (decoder) return decoder.decode(arrayBuffer, { stream: true })
    // 兜底（罕见场景）：把 ArrayBuffer 转 Uint8Array，再 Base64 → 解 UTF-8
    const u8 = new Uint8Array(arrayBuffer)
    let s = ''
    for (let i = 0; i < u8.length; i++) s += String.fromCharCode(u8[i])
    try { return decodeURIComponent(escape(s)) } catch (_) { return s }
  }

  const task = uni.request({
    url: BASE_URL + URL_PATH,
    method: 'POST',
    data: body,
    header: { 'Content-Type': 'application/json' },
    enableChunked: true,
    responseType: 'arraybuffer',
    success: () => { dispatcher.flush(); handlers.onDone?.() },
    fail:   (err) => handlers.onError?.(err),
  })
  if (task && task.onChunkReceived) {
    task.onChunkReceived((res) => {
      dispatcher.push(decodeChunk(res.data))
    })
  } else {
    // 基础库 <2.20.1：降级到非流式
    handlers.onError?.(new Error('mp-weixin enableChunked unsupported'))
  }
}
// #endif

export function streamAsk(body, handlers) {
  // #ifdef H5
  return streamAsk_H5(body, handlers)
  // #endif
  // #ifdef MP-WEIXIN
  return streamAsk_MP(body, handlers)
  // #endif
}
