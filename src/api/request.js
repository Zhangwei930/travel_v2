// 后端接口请求封装

export const BASE_URL = 'https://tr.magies.top/zhoumi-api'

export function request(path, { method = 'GET', data, header } = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + path,
      method,
      data,
      timeout: 20000,
      header: { 'Content-Type': 'application/json', ...header },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(new Error(`HTTP ${res.statusCode}`))
        }
      },
      fail: (err) => reject(err),
    })
  })
}
