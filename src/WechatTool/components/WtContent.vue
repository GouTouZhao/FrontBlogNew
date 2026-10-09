<template>
  <perfect-scrollbar>
    <div class="wt-content">
      <div class="wt-preview">
        <div class="phone-wrap" :style="{height: wrapperHeight + 'px'}">
          <div class="phone-scale" :style="{ transform: `scale(${phoneScale})` }">
            <div id="phone" class="phone" :class="[useSystemStore.appearance.model, {'dark': useSystemStore.appearance.darkMode}]" :style="phoneStyle">
              <PhoneBar :appearance="appearance" />
              <PhoneNav :appearance="appearance" />
              <div class="phone-bg">
                <img :src="useSystemStore.appearance.chatBackground" v-if="useSystemStore.appearance.chatBackground" class="phone-bg-for-height" />
              </div>
              <PhoneBody :appearance="appearance" :emojiBase64="emojiBase64" />
              <PhoneBottom :appearance="appearance" :emojiBase64="emojiBase64" />
            </div>
          </div>
        </div>
        <PhoneTools />
        <PhoneGenerate />
      </div>
    </div>
  </perfect-scrollbar>
</template>

<script setup>
import { ref, watch } from "vue";
import useStore from "@/WechatTool/store";
const { useSystemStore } = useStore();
import { models } from "@/WechatTool/utils/enum"
import PhoneBar from "./phone/PhoneBar.vue";
import PhoneNav from "./phone/PhoneNav.vue";
import PhoneBody from "./phone/PhoneBody.vue";
import PhoneBottom from "./phone/PhoneBottom.vue";
import PhoneGenerate from "./phone/PhoneGenerate.vue"
import PhoneTools from "./phone/PhoneTools.vue"
import emojiBase64 from "@/WechatTool/utils/emojiBase64";

const phoneWidth = ref(1080)
const phoneHeight = ref(2388)
const phoneScale = ref(1)
const appearance = ref({})
const wrapperHeight = ref(0)
const phoneStyle = ref({})
watch(() => useSystemStore.appearance, (newVal) => {
  // The phone keeps its source resolution; only the editor preview is scaled.
  // 做缩放是为了在预览时好看，同时在生成图片、视频时高清
  const model = 'android'
  if (newVal.model !== model) {
    useSystemStore.appearance.model = model
  }
  appearance.value = useSystemStore.appearance
  const { width, height } = models.find(item => item.value === model)
  useSystemStore.phoneWidth = phoneWidth.value = width
  useSystemStore.phoneHeight = phoneHeight.value = height
  useSystemStore.phoneScale = phoneScale.value = 360 / width
  wrapperHeight.value = height * phoneScale.value
  phoneStyle.value = {
    width: `${width}px`,
    height: `${height}px`,
    '--phone-bar-height': '105px',
    '--phone-nav-height': '141px',
    '--phone-content-top': '246px',
    '--phone-content-bottom': '167px',
    '--phone-bottom-height': '167px',
    '--phone-bottom-bar-display': 'none',
    '--phone-message-size': '42px',
    '--phone-message-min-height': '108px',
    '--phone-message-padding-y': '18px',
    '--phone-message-line-height': '59px',
    '--phone-message-tail-top': '36px',
    '--phone-avatar-size': '108px',
  }
}, {
  immediate: true,
})
</script>

<style lang="less" scoped>
.wt-content {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 10px;
  .wt-skeleton {
    width: 40%;
    padding: 10px;
    background-color: #F1F1F1;
  }
  .wt-preview {
    position: relative;

    .phone-wrap {
      width: 360px;
      height: 100%;
      .phone-scale {
        transform-origin: 0 0;
      }
      .phone {
        font-family: SF Pro, PingFang SC;
        font-weight: 400;
        -webkit-font-smoothing: antialiased;
        background-color: #ededed;
        position: relative;
        font-size: 36px;
        &.dark {
          background-color: var(--dark-bg-color);
          color: var(--dark-text-color);
        }
        .phone-bg {
          display: flex;
          align-items: center;
          justify-content: center;
          position: absolute;
          top: var(--phone-content-top, 264px);
          bottom: var(--phone-content-bottom, 269px);
          width: 100%;
          overflow: hidden;
          .phone-bg-for-height {
            width: 100%;
            max-width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }
      }
    }
  }
}</style>