<script setup>
import WechatApp from '../WechatTool/App.vue';
</script>

<template>
  <div class="wechat-tool-container reveal delay-100 visible">
    <WechatApp />
  </div>
</template>

<style scoped>
.wechat-tool-container {
  width: 100%;
  height: calc(100vh - 80px);
  background-color: var(--bg-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--glass-shadow);
  border: 1px solid var(--border-color);
}
</style>
