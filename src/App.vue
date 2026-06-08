<script>
import { ensureDefaultProfile } from './api/storage.js'
import { api } from './api/index.js'

export default {
  onLaunch() {
    ensureDefaultProfile()
    // 拉取后台配置，决定是否展示在线咨询入口（默认关闭）
    api.getCapability().then((c) => {
      const on = !!(c && c.consult)
      try { uni.setStorageSync('zhoumi_consult_on', on) } catch (_) {}
      uni.$emit('consultFlag', on)
    }).catch(() => {})
  },
  onShow() {},
  onHide() {},
}
</script>

<style lang="scss">
@import './uni.scss';

page {
  background-color: $z-bg;
  font-family: $sans;
  color: $z-text;
  -webkit-font-smoothing: antialiased;
}

view, text, input, button, image, scroll-view {
  box-sizing: border-box;
}

::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
  background: transparent;
}

// ── 工具类 ──────────────────────────────────────────────────

.serif { font-family: $serif; }
.mono  { font-family: $mono; }

.card {
  background: $z-card;
  border-radius: $radius-card;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
}

.btn-accent {
  background: linear-gradient(135deg, $z-accent 0%, $z-accent-l 100%);
  box-shadow: 0 12rpx 36rpx rgba(255, 107, 53, 0.44);
  color: $z-card;
  border-radius: $radius-btn;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, $z-primary 0%, $z-primary-m 100%);
  box-shadow: 0 6rpx 20rpx rgba(13, 79, 74, 0.33);
  color: $z-card;
  border-radius: $radius-btn;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 4rpx 16rpx;
  border-radius: $radius-tag;
  font-size: $font-xs;
  font-weight: 600;
  white-space: nowrap;
}

.safe-bottom {
  height: constant(safe-area-inset-bottom);
  height: env(safe-area-inset-bottom);
}

// ── 章节标题通用 §──────────────────────────────────────────

.sec-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 22rpx;

  .sec-left {
    display: flex;
    align-items: baseline;
    gap: 16rpx;
  }

  .sec-no {
    font-family: $mono;
    font-size: $font-mono;
    color: $z-muted;
    font-weight: 700;
    letter-spacing: 1rpx;
  }

  .sec-title {
    font-family: $serif;
    font-size: 30rpx;
    font-weight: 800;
    color: $z-text;
    line-height: 1.2;
  }

  .sec-sub {
    font-size: $font-mono;
    color: $z-muted;
    margin-top: 2rpx;
  }

  .sec-action {
    font-size: 23rpx;
    color: $z-primary;
    font-weight: 600;
  }
}
</style>
