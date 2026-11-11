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
import { ref, watch, onMounted } from "vue";
import useStore from "@/WechatTool/store";
const { useSystemStore } = useStore();
import { models, getModelConfig } from "@/WechatTool/utils/enum"
import PhoneBar from "./phone/PhoneBar.vue";
import PhoneNav from "./phone/PhoneNav.vue";
import PhoneBody from "./phone/PhoneBody.vue";
import PhoneBottom from "./phone/PhoneBottom.vue";
import PhoneGenerate from "./phone/PhoneGenerate.vue"
import PhoneTools from "./phone/PhoneTools.vue"
import emojiBase64 from "@/WechatTool/utils/emojiBase64";

const phoneWidth = ref(1256)
const phoneHeight = ref(2760)
const phoneScale = ref(1)
const appearance = ref({})
const wrapperHeight = ref(0)
const phoneStyle = ref({})

const applyModelConfig = (modelVal) => {
  const currentModel = getModelConfig(modelVal)
  const { width, height } = currentModel
  useSystemStore.phoneWidth = phoneWidth.value = width
  useSystemStore.phoneHeight = phoneHeight.value = height
  useSystemStore.phoneScale = phoneScale.value = 360 / width
  wrapperHeight.value = height * phoneScale.value
  phoneStyle.value = {
    width: `${width}px`,
    height: `${height}px`,
    '--phone-bar-height': `${currentModel.barHeight}px`,
    '--phone-nav-height': `${currentModel.navHeight}px`,
    '--phone-content-top': `${currentModel.contentTop}px`,
    '--phone-content-bottom': `${currentModel.contentBottom}px`,
    '--phone-bottom-height': `${currentModel.bottomHeight}px`,
    '--phone-bottom-bar-display': currentModel.bottomBarDisplay || 'none',
    '--phone-message-size': `${currentModel.messageSize}px`,
    '--phone-message-min-height': `${currentModel.messageMinHeight}px`,
    '--phone-message-padding-y': `${currentModel.messagePaddingY}px`,
    '--phone-message-padding-x': `${currentModel.messagePaddingX}px`,
    '--phone-message-line-height': `${currentModel.messageLineHeight}px`,
    '--phone-message-tail-top': `${currentModel.messageTailTop}px`,
    '--phone-avatar-size': `${currentModel.avatarSize}px`,
    '--phone-bar-icon-top': `${currentModel.barIconTop}px`,
    '--phone-bubble-margin-near': `${currentModel.bubbleMarginNear}px`,
    '--phone-bubble-margin-far': `${currentModel.bubbleMarginFar}px`,
    '--phone-username-size': `${currentModel.usernameSize}px`,
    '--phone-username-margin-left': `${currentModel.usernameMarginLeft}px`,
    '--phone-revoke-size': `${currentModel.revokeSize}px`,
    '--phone-revoke-weight': currentModel.revokeWeight || '500',
    '--phone-time-size': `${currentModel.timeSize}px`,
    '--phone-time-weight': currentModel.timeWeight || 'normal',
    '--phone-item-padding-y': `${currentModel.itemPaddingY}px`,
    '--phone-time-padding-top': `${currentModel.timePaddingTop}px`,
    '--phone-time-padding-bottom': `${currentModel.timePaddingBottom}px`,
    '--phone-nav-title-size': `${currentModel.navTitleSize}px`,
    '--phone-nav-title-weight': currentModel.navTitleWeight || '500',
    '--phone-time-after-revoke-reduce': `${currentModel.timeAfterRevokeReduce || 0}px`,
    '--phone-time-before-revoke-reduce': `${currentModel.timeBeforeRevokeReduce || 0}px`,
    '--phone-revoke-after-time-reduce': `${currentModel.revokeAfterTimeReduce || 0}px`,
    '--phone-time-letter-spacing': `${currentModel.timeLetterSpacing || 0}px`,
    '--phone-revoke-letter-spacing': `${currentModel.revokeLetterSpacing || 0}px`,
    '--phone-av-icon-width': `${currentModel.avIconWidth || 50}px`,
    '--phone-av-icon-height': `${currentModel.avIconHeight || 21}px`,
    '--phone-av-icon-top': `${currentModel.avIconTop ?? 2}px`,
    '--phone-nav-earphone-width': `${currentModel.navEarphoneWidth || 36}px`,
    '--phone-nav-earphone-height': `${currentModel.navEarphoneHeight || 44}px`,
    '--phone-nav-earphone-margin-top': `${currentModel.navEarphoneMarginTop ?? 8}px`,
  }
}

onMounted(() => {
  // 首次升级到多机型时，优先展示新机型“华为俊秀”，便于立即查看效果
  if (!localStorage.getItem('wechat_tool_model_initialized')) {
    useSystemStore.appearance.model = 'huawei_junxiu'
    localStorage.setItem('wechat_tool_model_initialized', '1')
  }
  applyModelConfig(useSystemStore.appearance.model)
})

watch(() => useSystemStore.appearance.model, (newModel) => {
  applyModelConfig(newModel)
}, {
  immediate: true,
})

watch(() => useSystemStore.appearance, (newVal) => {
  appearance.value = newVal
}, {
  immediate: true,
  deep: true,
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