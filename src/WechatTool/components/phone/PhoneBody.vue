<template>
  <div class="phone-body" :class="{'dark': appearance.darkMode}" ref="phoneBodyRef" @contextmenu.stop="handlePhoneBodyContextMenu">
    <div class="wechat-content">
      <div class="wechat-item" :id="chat.id" v-for="chat in useChatStore.chatList" :key="chat.id" :class="{'wechat-item-right': chat.role === 'own', 'wechat-item-rejected': chat.role === 'own' && chat.rejected, 'wechat-item-notice-box': !showAvatar(chat), 'wechat-item-time-box': chat.type === 'time', 'active': useContextMenuStore.activeChatId === chat.id}" @contextmenu.stop="e => rightClicked(e, chat.id)">
        <div class="wechat-item-avatar" v-if="showAvatar(chat)">
          <img :src="getUser(chat).avatar" alt="">
        </div>
        <div>
          <div class="wechat-item-name" v-if="useSystemStore.appearance.showChatName && !['time', 'takeAPat', 'revoke', 'system'].includes(chat.type)">
            {{ getUser(chat).nickname }}
          </div>
          <div class="wechat-item-text" v-if="chat.type === 'text'" v-html="renderText(chat.content, emojiBase64)"></div>
          <div class="wechat-item-text wechat-item-image" v-else-if="chat.type === 'image'">
            <img :src="chat.content" alt="">
          </div>
          <div class="wechat-item-text wechat-item-trans" :class="{'wechat-item-trans-received': chat.received}" v-else-if="chat.type === 'transferAccounts'">
            <div class="wechat-item-trans-content">
              <i></i> 
              <div>
                <span>¥{{ chat.money.toFixed(2) }}</span> 
                <span class="font" v-if="chat.received">已被领取</span>
                <span class="font" v-else-if="!chat.content">转账给{{ chat.role === 'own' ? useUserStore.activeUser.nickname : "你" }}</span>
                <span class="font" v-else>{{ chat.content }}</span>
              </div>
            </div>
            <div class="wechat-item-trans-bottom">
              <span>微信转账</span>
            </div>
          </div>
          <div class="wechat-item-text wechat-item-trans" :class="{'wechat-item-trans-received': chat.received}" v-else-if="chat.type === 'redEnvelope'">
            <div class="wechat-item-trans-content wechat-item-redp-content">
              <i></i> 
              <div>
                <!-- <span>¥{{ chat.money.toFixed(2) }}</span>  -->
                <span>{{ chat.content || "恭喜发财，大吉大利" }}</span>
                <span class="font" v-if="chat.received">已领取</span>
              </div>
            </div>
            <div class="wechat-item-trans-bottom">
              <span>微信红包</span>
            </div>
          </div>
          <div class="wechat-item-notice" v-else-if="chat.type === 'receive' && chat.receivedChatType === 'redEnvelope'">
            <i></i>{{ chat.role === 'own' ? "你" : useUserStore.activeUser.nickname }}领取了{{ chat.role === 'own' ? useUserStore.activeUser.nickname : "你" }}的<em>红包</em>
          </div>
          <div class="wechat-item-text wechat-item-trans wechat-item-trans-received" v-else-if="chat.type === 'receive' && chat.receivedChatType === 'transferAccounts'">
            <div class="wechat-item-trans-content">
              <i></i> 
              <div>
                <span>¥{{ chat.money.toFixed(2) }}</span> 
                <span class="font">已收款</span>
              </div>
            </div>
            <div class="wechat-item-trans-bottom">
              <span>微信转账</span>
            </div>
          </div>
          <!-- <div class="wechat-item-text wechat-item-voice" v-else-if="chat.type === 'voice'">
            <i></i> 
            <span>{{ chat.duration }}"</span>
            <div :style="{width: chat.duration * 5 + 'px'}"></div>
            <em v-if="!chat.received"></em>
          </div> -->
          <div class="wechat-item-voice-wrapper" v-else-if="chat.type === 'voice'">
            <div class="wechat-item-text wechat-item-voice" :style="{ width: `${voiceWidth(chat)}px` }">
              <i></i> 
              <span>{{ chat.duration }}"</span>
              <em v-if="!chat.received"></em>
            </div>
            <div class="wechat-item-text wechat-item-voice-text" v-if="chat.content">{{ chat.content }}</div>
          </div>
          <div class="wechat-item-text wechat-item-av" v-else-if="chat.type === 'avInvite'">
            <i :class="[chat.invateType]"></i>
            <span v-if="chat.state === 'success'">通话时长 {{ chat.duration }}</span>
            <span v-else>{{ chat.role === "other" ? "对方" : "" }}{{ filterLabel(avInviteStates, chat.state) }}</span>
          </div>
          <div class="wechat-item-text wechat-item-businessCard" v-else-if="chat.type === 'businessCard'">
            <div class="info">
              <img :src="chat.image" alt="">
              <p>{{ chat.content }}</p>
            </div>
            <span>个人名片</span>
          </div>
          <div class="wechat-item-notice" :class="{'bg': !['time', 'revoke'].includes(chat.type), 'bold': chat.type === 'takeAPat' && chat.patBold}" v-else-if="['time', 'takeAPat', 'revoke', 'system'].includes(chat.type)">
            <span v-if="chat.type !== 'revoke'">{{ chat.content }}</span>
            <span v-else style="font-size: 34px; font-weight: 500;">{{ chat.role === 'own' ? "你" : useUserStore.activeUser.nickname }}撤回了一条消息</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import useStore from "@/WechatTool/store";
const { useSystemStore, useUserStore, useChatStore, useContextMenuStore } = useStore();
import useAutoScrollBottom from "@/WechatTool/hooks/useAutoScrollBottom";
import { renderText, filterLabel } from "@/WechatTool/utils/utils";
import { avInviteStates } from "@/WechatTool/utils/enum";

const getUser = (chat) => {
  if (!chat || !chat.user || !chat.user.id) return chat?.user || {};
  const found = useUserStore.userList.find(u => u.id === chat.user.id);
  return found || chat.user;
};

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

const handlePhoneBodyContextMenu = (e) => {
  e.preventDefault();
  useContextMenuStore.hideContextMenu();
  useContextMenuStore.activeChatId = "";
}

const rightClicked = (e, chatId) => {
  e.preventDefault();
  useContextMenuStore.showContextMenu(e.clientX, e.clientY, chatId);
};

const phoneBodyRef = ref(null)
useAutoScrollBottom(phoneBodyRef)

// watch(() => useContextMenuStore.activeChatId, (newVal) => {
//   if (newVal) {
//     const targetElement = document.getElementById(newVal);
//     if (targetElement) {
//       targetElement.scrollIntoView({
//         behavior: "smooth",
//         block: "nearest", // start center end nearest
//       });
//     }
//   }
// })

const showAvatar = (chat) => {
  return !['time', 'takeAPat', 'revoke', 'system'].includes(chat.type) && !(chat.type === 'receive' && chat.receivedChatType === 'redEnvelope') 
}

const voiceWidth = (chat) => {
  const duration = Math.min(60, Math.max(1, Math.round(Number(chat.duration) || 1)));
  let segments = 0;
  if (duration <= 10) {
    segments = duration - 1;
  } else {
    // 11~19和10一样长，20~29加一段，30~39加一段，40~49加一段，50~59加一段，60加最后一段
    segments = 8 + Math.floor(duration / 10);
  }
  const minWidth = 203;
  const maxWidth = 550;
  const totalSegments = 14;
  return minWidth + segments * ((maxWidth - minWidth) / totalSegments);
}
</script>

<style lang="less" scoped>
::-webkit-scrollbar {
  display: none;
}
.phone-body {
  color: #171717;
  position: absolute;
  top: var(--phone-content-top, 264px);
  bottom: var(--phone-content-bottom, 269px);
  left: 0;
  right: 0;
  -webkit-overflow-scrolling: touch;
  overflow-x: hidden;
  overflow-y: scroll;
  .wechat-content {
    padding-top: 42px;
    .wechat-item {
      padding: 16px 36px;
      position: relative;
      display: flex;
      &:hover, &.active {
        background-color: rgba(0, 0, 0, .15);
      }
      .wechat-item-name {
        margin: 0 0 12px 162px;
        font-size: 42px;
      }
      .wechat-item-avatar {
        width: var(--phone-avatar-size, 123px);
        height: var(--phone-avatar-size, 123px);
        background: #f1f1f1;
        border-radius: 15px;
        background-size: cover;
        background-repeat: no-repeat;
        position: absolute;
        background-position: center;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }
      .wechat-item-voice-wrapper {
        display: flex;
        flex-direction: column;
      }
      .wechat-item-text {
        background: #ffffff;
        box-sizing: border-box;
        padding: var(--phone-message-padding-y, 28px) 38px;
        font-size: var(--phone-message-size, 48px);
        border-radius: 15px;
        margin-right: 140px;
        word-break: break-all;
        margin-left: 133px;
        display: inline-flex;
        position: relative;
        line-height: var(--phone-message-line-height, normal);
        min-height: var(--phone-message-min-height, 123px);
        align-items: center;
        .emoji-img {
          width: 24px !important;
          height: 24px !important;
        }
        &:after {
          content: '';
          background: #fff;
          width: 24px;
          height: 24px;
          border-bottom-left-radius: 4px;
          top: var(--phone-message-tail-top, 50px);
          left: -12px;
          position: absolute;
          transform: rotate(45deg);
        }
        &.wechat-item-image {
          border: 1px #d5d5d5 solid;
          padding: 0;
          background: none !important;
          img {
            max-width: 420px;
            max-height: 420px;
            border-radius: 15px;
            overflow: hidden;
          }
          &:after {
            display: none;
          }
        }
        &.wechat-item-trans {
          background: #f79c46 !important;
          width: 700px;
          padding-top: 0;
          padding-bottom: 0;
          .wechat-item-trans-content {
            display: flex;
            height: 192px;
            align-items: center;
            position: relative;
            i {
              width: 120px;
              height: 120px;
              background: url(@/WechatTool/assets/images/content/wechat-trans-icon1.png) no-repeat;
            }
            div {
              flex: 1;
              display: flex;
              flex-direction: column;
              margin-left: 30px;
              overflow: hidden;
              span {
                font-size: 48px;
                color: #fff;
                margin-top: -5px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
              }
              .font {
                font-size: 36px;
                color: #fff;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                margin-top: 4px;
              }
            }
          }
          .wechat-item-redp-content {
            i {
              width: 102px;
              margin-left: 9px;
              background: url(@/WechatTool/assets/images/content/wechat-trans-icon3.png) no-repeat;
            }
          }
          .wechat-item-trans-bottom {
            height: 71px;
            align-items: center;
            display: flex;
            span {
              font-size: 36px;
              color: #faecda;
            }
          }
          &:after {
            content: '';
            background: #f79c46 !important;
          }
        }
        &.wechat-item-trans-received {
          background: #f8e2c6 !important;
          .wechat-item-trans-content {
            i {
              background: url(@/WechatTool/assets/images/content/wechat-trans-icon2.png) no-repeat;
            }
          }
          .wechat-item-redp-content {
            i {
              background: url(@/WechatTool/assets/images/content/wechat-trans-icon4.png) no-repeat;
            }
          }
          .wechat-item-trans-bottom {
            span {
              color: #FFFFFF;
            }
          }
          &:after {
            background: #f8e2c6 !important;
          }
        }
        &.wechat-item-voice {
          display: flex;
          padding-left: 23px;
          span {
            font-size: 40px;
            padding-right: 20px;
            width: 120px;
          }
          i {
            width: 34px;
            height: 42px;
            flex: 0 0 34px;
            position: relative;
            z-index: 1;
            background: url(@/WechatTool/assets/images/content/wechat-voice-icon1-light.png) no-repeat;
            background-size: 100% 100%;
            margin-right: 18px;
            margin-left: 0px;
          }
          em {
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: #e75e58;
            position: absolute;
            right: -61px;
          }
        }
        &.wechat-item-voice-text {
          text-align: justify;
          margin-top: 20px;
          &:after {
            display: none;
          }
        }
        &.wechat-item-av {
          display: flex;
          align-items: center;
          padding-right: 36px;
          span {
            margin: 0 0 0 12px;
          }
          i {
            display: block;
            position: relative;
            top: 2px;
            width: 50px;
            height: 28px;
            background-image: url(@/WechatTool/assets/images/content/wechat-audio-light.png);
            background-repeat: no-repeat;
            background-size: 100%;
            margin: 0 12px 0 0;
            &.video {
              width: 50px;
              height: 38px;
              background-image: url(@/WechatTool/assets/images/content/wechat-video-light.png);
            }
          }
        }
        &.wechat-item-businessCard {
          padding: 28px 28px 0;
          width: 60%;
          .info {
            display: flex;
            align-items: center;
            border-bottom: 1px solid #E9E9E9;
            padding-bottom: 28px;
            img {
              width: 108px;
              border-radius: 12px;
              margin-right: 28px;
            }
            p {
              margin: 0;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }
          span {
            position: relative;
            font-size: 28px;
            top: -8px;
          }
        }
      }
      &.wechat-item-right {
        justify-content: flex-end;
        .wechat-item-name {
          display: none;
        }
        .wechat-item-face {
          right: 0;
        }
        .wechat-item-voice-wrapper {
          align-items: end;
        }
        .wechat-item-text {
          background: #95ec6a;
          margin-left: 140px;
          margin-right: 133px;
          &:after {
            background: #95ec6a;
            left: auto;
            right: -10px;
            border-top-right-radius: 4px;
            border-bottom-left-radius: 0;
          }
          &.wechat-item-voice {
            flex-direction: row-reverse;
            padding-left: 38px;
            padding-right: 23px;
            span {
              padding-left: 20px;
              padding-right: 0;
              text-align: right;
            }
            i {
              background: url(@/WechatTool/assets/images/content/wechat-voice-icon2-light.png) no-repeat;
              background-size: 100% 100%;
              margin-left: 18px;
              margin-right: 0;
            }
            em {
              left: -61px;
            }
          }
          &.wechat-item-voice-text {
            color: var(--dark-text-color) !important;
          }
          &.wechat-item-av {
            flex-direction: row-reverse;
            padding-left: 36px;
            padding-right: 38px;
            span {
              margin: 0 12px 0 0;
            }
            i {
              margin: 0 0 0 12px;
              &.video {
                background-image: url(@/WechatTool/assets/images/content/wechat-video-light.png);
              }
            }
          }
          &.wechat-item-businessCard {
            background-color: #FFF;
            &:after {
              background: #FFF;
            }
          }
        }
      }
      &.wechat-item-notice-box {
        padding: 12px 38px;
        justify-content: center;
        &.wechat-item-time-box {
          padding-top: 38px;
          padding-bottom: 38px;
        }
        .wechat-item-notice {
          font-size: 32px;
          font-weight: 50;
          color: #a6a6a6;
          span {
            display: inline-block; /* 必须加上这个，transform 才会生效 */
            transform: scaleX(0.95); /* 改变这个数值，0.85 会让字变得瘦长 */
          }
          justify-content: center;
          padding: 12px 16px 10px;
          border-radius: 6px;
          display: flex;
          align-items: center;
          &.bg {
            color: var(--light-text-color);
            background-color: rgba(255, 255, 255, 0.6);
          }
          &:not(.bg) {
            padding-top: 0;
            padding-bottom: 0;
          }
          &.bold {
            span {
              font-weight: bold;
            }
          }
          i {
            width: 45px;
            height: 51px;
            background: url(@/WechatTool/assets/images/content/wechat-redp-icon1.png) no-repeat;
            margin-right: 18px;
            margin-top: -5px;
          }
          em {
            font-style: normal;
            color: #ef9d49;
          }
        }
      }
      &.wechat-item-rejected {
        .wechat-item-text:not(.wechat-item-voice-text) {
          position: relative;
          &:before {
            content: "!";
            position: absolute;
            width: 64px;
            text-align: center;
            height: 64px;
            line-height: 64px;
            left: -91px;
            top: 50%;
            margin-top: -32px;
            font-size: 42px;
            color: var(--dark-text-color);
            border-radius: 50%;
            background-color: #FA5151;
          }
          &.wechat-item-voice {
            em {
              display: none;
            }
          }
        }
      }
    }
  }
  &.dark {
    .wechat-content {
      .wechat-item {
        &:hover, &.active {
          background-color: rgba(255, 255, 255, .15);
        }
        .wechat-item-text {
          background: #2b2b2b;
          color: #d5d5d5;
          &:after {
            content: '';
            background: #2b2b2b;
          }
          &.wechat-item-voice {
            i {
              background: url(@/WechatTool/assets/images/content/wechat-voice-icon1-dark.png) no-repeat;
              background-size: 100% 100%;
            }
          }
          &.wechat-item-av {
            i {
              background-image: url(@/WechatTool/assets/images/content/wechat-audio-dark.png);
              &.video {
                background-image: url(@/WechatTool/assets/images/content/wechat-video-dark.png);
              }
            }
          }
        }
        &.wechat-item-right {
          .wechat-item-text {
            background: #3eb575;
            color: #000;
            &:after {
              background: #3eb575;
            }
            &.wechat-item-voice {
              i {
                background: url(@/WechatTool/assets/images/content/wechat-voice-icon2-light.png) no-repeat;
                background-size: 100% 100%;
              }
            }
            &.wechat-item-av {
              i {
                background-image: url(@/WechatTool/assets/images/content/wechat-audio-light.png);
                &.video {
                  background-image: url(@/WechatTool/assets/images/content/wechat-video-light.png);
                }
              }
            }
          }
        }
      }
    }
  }
}
</style>