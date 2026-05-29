<template>
  <image
    class="cy-icon"
    :src="src"
    :style="{ width: size + 'rpx', height: size + 'rpx' }"
    mode="aspectFit"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
  size: { type: Number, default: 48 },
})

const src = computed(() => `/static/images/ui/${props.name}.svg`)
</script>

<style lang="scss">
.cy-icon {
  display: inline-flex;
  flex-shrink: 0;
}
</style>
