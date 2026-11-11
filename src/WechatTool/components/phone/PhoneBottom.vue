<template>
  <div class="phone-bottom" :class="{'dark': appearance.darkMode, 'huawei-bottom': isHuawei}">
    <div class="phone-bottom-chat">
      <div class="wechat-bottom-icon" :class="[appearance.voiceMode ? 'wechat-voice-say-icon' : 'wechat-voice-icon']">
        语音
      </div>
      <div class="wechat-input" :class="{'wechat-input-say': appearance.voiceMode, 'wechat-input-sync': !appearance.voiceMode && appearance.syncInputText}">
        <span class="wechat-input-text" v-html="wechatInput"></span>
        <div v-if="showVoiceInputIcon" class="wechat-input-voice-btn" aria-label="语音输入">
          <svg :viewBox="voiceInputIcon.viewBox" width="100%" height="100%" fill="currentColor">
            <path v-for="(p, i) in voiceInputIcon.paths" :key="i" :d="p.d" :transform="p.transform" />
          </svg>
        </div>
      </div>
      <div class="wechat-bottom-icon wechat-emoji-icon">表情</div>
      <div class="wechat-bottom-icon" :class="[!appearance.voiceMode && appearance.syncInputText && useChatStore.inputText && useUserStore.activeRole === 'own' ? 'wechat-bottom-sync': 'wechat-more-icon']">发送</div>
    </div>
    <div class="phone-bottom-bar"><i>返回桌面</i></div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue"
import useStore from "@/WechatTool/store";
const { useChatStore, useUserStore, useSystemStore } = useStore();
import { renderText } from "@/WechatTool/utils/utils";
import { voiceInputIcon } from "./bottomIcons";

const props = defineProps({
  appearance: {
    type: Object,
    default: () => {},
  },
  emojiBase64: {
    type: Object,
    default: () => {},
  },
})

const wechatInput = ref("")
watch(() => [props.appearance.voiceMode, useChatStore.inputText, useUserStore.activeRole], () => {
  if (props.appearance.voiceMode) {
    wechatInput.value = "按住 说话"
  } else if (useUserStore.activeRole === "other") {
    wechatInput.value = ""
  } else {
    wechatInput.value = renderText(useChatStore.inputText, props.emojiBase64)
  }
}, {
  immediate: true,
})

const showVoiceInputIcon = computed(() => {
  if (props.appearance.voiceMode) return false;
  if (props.appearance.syncInputText && useChatStore.inputText && useUserStore.activeRole === 'own') {
    return false;
  }
  return true;
});

const isHuawei = computed(() => {
  const m = props.appearance?.model || useSystemStore.appearance?.model;
  return m === 'huawei_junxiu';
});
</script>

<style lang="less" scoped>
.phone-bottom {
  background: #f6f6f6;
  position: absolute;
  bottom: 0;
  width: 100%;
  height: var(--phone-bottom-height, 269px);
  .phone-bottom-chat {
    height: 152px;
    display: flex;
    align-items: center;
    color: var(--light-text-color);
    .wechat-bottom-icon {
      width: 80px;
      height: 80px;
      text-indent: -9999px;
      &.wechat-voice-say-icon {
        background: url(@/WechatTool/assets/images/bottom/wechat-bottom-icon4-light.png)
          no-repeat;
        margin-left: 32px;
      }
      &.wechat-voice-icon {
        background: url(@/WechatTool/assets/images/bottom/wechat-bottom-icon1-light.png)
          no-repeat;
        margin-left: 32px;
      }
      &.wechat-emoji-icon {
        background: url(@/WechatTool/assets/images/bottom/wechat-bottom-icon2-light.png)
          no-repeat;
      }
      &.wechat-more-icon {
        background: url(@/WechatTool/assets/images/bottom/wechat-bottom-icon3-light.png)
          no-repeat;
        margin: 0 32px 0 39px;
      }
      &.wechat-bottom-sync {
        text-indent: 0;
        font-size: 48px;
        text-align: center;
        height: 88px;
        line-height: 88px;
        width: 160px;
        margin: 0 24px;
        border-radius: 16px;
        background-color: #05C160;
        color: #FFF;
      }
    }
    .wechat-input {
      height: 120px;
      background: #fff;
      border-radius: 15px;
      flex: 1;
      margin: 0 32px;
      position: relative;
      display: flex;
      align-items: center;

      .wechat-input-text {
        width: 100%;
        display: none;
        font-size: 48px;
        font-weight: 500;
        line-height: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .wechat-input-voice-btn {
        position: absolute;
        right: 24px;
        top: 50%;
        transform: translateY(-50%);
        width: 41.4px;
        height: 55px;
        color: #747474;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
      }
    }
    .wechat-input-say {
      justify-content: center;
      .wechat-input-text {
        display: block;
        text-align: center;
        font-size: 48px;
        font-weight: 500;
        line-height: 120px;
      }
    }
    .wechat-input-sync {
      .wechat-input-text {
        display: flex;
        align-items: center;
        font-size: 48px;
        font-weight: 500;
        line-height: 120px;
        padding-left: 0.6em;
        padding-right: 75px;
        overflow: hidden;
      }
    }
  }
  .phone-bottom-bar {
    height: 102px;
    display: flex;
    display: var(--phone-bottom-bar-display, flex);
    justify-content: center;
    i {
      width: 402px;
      height: 15px;
      background: url(@/WechatTool/assets/images/bottom/phone-bottom-bar-light.png) no-repeat;
      margin-top: 63px;
      text-indent: -9999px;
    }
  }
  &.dark {
    background: var(--dark-bg-color);
    .phone-bottom-chat {
      color: var(--dark-text-color);
      .wechat-bottom-icon {
        &.wechat-voice-say-icon {
          background: url(@/WechatTool/assets/images/bottom/wechat-bottom-icon4-dark.png) no-repeat;
        }
        &.wechat-voice-icon {
          background: url(@/WechatTool/assets/images/bottom/wechat-bottom-icon1-dark.png) no-repeat;
        }
        &.wechat-emoji-icon {
          background: url(@/WechatTool/assets/images/bottom/wechat-bottom-icon2-dark.png) no-repeat;
        }
        &.wechat-more-icon {
          background: url(@/WechatTool/assets/images/bottom/wechat-bottom-icon3-dark.png) no-repeat;
        }
      }
      .wechat-input {
        background: #2b2b2b;
        .wechat-input-voice-btn {
          color: rgba(255, 255, 255, 0.45);
        }
      }
    }
    .phone-bottom-bar {
      i {
        background: url(@/WechatTool/assets/images/bottom/phone-bottom-bar-dark.png) no-repeat;
      }
    }
  }

  &.huawei-bottom {
    .phone-bottom-chat {
      position: relative;
      top: 10px;

      .wechat-emoji-icon {
        margin-right: 10px;
      }
    }
  }
}
</style>
