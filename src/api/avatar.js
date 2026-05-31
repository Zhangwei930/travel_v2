function isRemoteFile(path) {
  return /^https?:\/\//.test(path || '') && !/^https?:\/\/tmp\//.test(path || '')
}

function canUseWechatFileApi() {
  return typeof wx !== 'undefined' && typeof wx.getFileSystemManager === 'function'
}

function saveAvatarFile(tempFilePath) {
  if (!tempFilePath || !canUseWechatFileApi()) return Promise.resolve(tempFilePath || '')

  return new Promise((resolve) => {
    try {
      wx.getFileSystemManager().saveFile({
        tempFilePath,
        success: (res) => resolve(res.savedFilePath || tempFilePath),
        fail: () => resolve(tempFilePath),
      })
    } catch (_) {
      resolve(tempFilePath)
    }
  })
}

function downloadAvatarFile(url) {
  if (!url || typeof uni === 'undefined' || typeof uni.downloadFile !== 'function') {
    return Promise.resolve('')
  }

  return new Promise((resolve) => {
    uni.downloadFile({
      url,
      success: (res) => {
        const isOk = !res.statusCode || (res.statusCode >= 200 && res.statusCode < 300)
        resolve(isOk ? (res.tempFilePath || res.filePath || '') : '')
      },
      fail: () => resolve(''),
    })
  })
}

export async function cacheAvatarFile(path) {
  if (!path) return ''
  if (!canUseWechatFileApi()) return path

  const tempFilePath = isRemoteFile(path) ? await downloadAvatarFile(path) : path
  if (!tempFilePath) return path
  return saveAvatarFile(tempFilePath)
}
