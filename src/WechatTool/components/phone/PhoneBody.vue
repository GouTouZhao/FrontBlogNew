<template>
  <div class="phone-body" :class="{'dark': appearance.darkMode, 'huawei-body': isHuawei}" ref="phoneBodyRef" @contextmenu.stop="handlePhoneBodyContextMenu">
    <div class="wechat-content">
      <div class="wechat-item" :id="chat.id" v-for="(chat, index) in useChatStore.chatList" :key="chat.id" :class="{
        'wechat-item-right': chat.role === 'own',
        'wechat-item-rejected': chat.role === 'own' && chat.rejected,
        'wechat-item-notice-box': !showAvatar(chat),
        'wechat-item-time-box': chat.type === 'time',
        'wechat-item-time-after-revoke': isTimeAfterRevoke(index),
        'wechat-item-time-before-revoke': isTimeBeforeRevoke(index),
        'wechat-item-revoke-after-time': isRevokeAfterTime(index),
        'wechat-item-notice-after-time': isNoticeAfterTime(index),
        'wechat-item-time-after-notice': isTimeAfterNotice(index),
        'wechat-item-time-before-notice': isTimeBeforeNotice(index),
        'wechat-item-notice-after-notice': isNoticeAfterNotice(index),
        'active': useContextMenuStore.activeChatId === chat.id
      }" @contextmenu.stop="e => rightClicked(e, chat.id)">
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
              <span class="voice-duration"><span class="voice-num">{{ chat.duration }}</span><span class="voice-unit">"</span></span>
              <em v-if="!chat.received"></em>
            </div>
            <div class="wechat-item-text wechat-item-voice-text" v-if="chat.content">{{ chat.content }}</div>
          </div>
          <div class="wechat-item-text wechat-item-av" v-else-if="chat.type === 'avInvite'">
            <i :class="[chat.invateType]"></i>
            <span v-if="chat.state === 'success'"><span class="av-label">通话时长</span><span class="av-num">{{ chat.duration }}</span></span>
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
            <template v-if="chat.type === 'time'">
              <span class="wechat-item-time-content">
                <template v-for="(part, pIndex) in parseTimeSegments(chat.content)" :key="pIndex">
                  <!-- 粗细判断：数字部分 (part.isNum) vs 文字部分 (非数字)，粗细可在下方 style 中通过 -webkit-text-stroke 标签调节 -->
                  <span
                    v-if="part.isNum"
                    class="time-num"
                    :class="{
                      'time-num-after-ap': part.isAfterAp,
                      'time-num-hour': part.isClockHour,
                      'time-num-colon': part.isClockColon,
                      'time-num-minute': part.isClockMinute
                    }"
                  >{{ part.text }}</span>
                  <span v-else class="time-text">{{ part.text }}</span>
                </template>
              </span>
            </template>
            <span v-else-if="chat.type !== 'revoke'">{{ chat.content }}</span>
            <span v-else class="wechat-item-revoke">{{ chat.role === 'own' ? "你" : useUserStore.activeUser.nickname }}撤回了一条消息</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import useStore from "@/WechatTool/store";
const { useSystemStore, useUserStore, useChatStore, useContextMenuStore } = useStore();
import useAutoScrollBottom from "@/WechatTool/hooks/useAutoScrollBottom";
import { renderText, filterLabel } from "@/WechatTool/utils/utils";
import { avInviteStates } from "@/WechatTool/utils/enum";

// 格式化时间戳内容：如 09:56 或 09：56 去除小时前导0，直接显示 9:56
const formatTimeContent = (content) => {
  if (!content) return "";
  return String(content).replace(/(^|[^\d])0([1-9][:：]\d{2})/g, '$1$2');
};

// 解析时间戳内容，将数字部分与汉字/文字部分区分，并将时钟的小时、冒号、分钟独立拆段以便微调间距
const parseTimeSegments = (rawContent) => {
  const content = formatTimeContent(rawContent);
  if (!content) return [];
  const str = String(content);
  // 按连续数字（包含时间冒号）与非数字文字切分
  const matches = str.match(/([0-9]+(?:[:：][0-9]+)*|[^0-9]+)/g) || [str];
  const segments = [];
  matches.forEach((part, index) => {
    const isNum = /[0-9]/.test(part);
    // 判断该时间数字前面是否紧邻“上午/下午”文字
    const prevText = index > 0 ? matches[index - 1] : "";
    const isAfterAp = isNum && /(?:上午|下午|中午|晚上|凌晨|傍晚)\s*$/.test(prevText);
    if (isNum && /[:：]/.test(part)) {
      const subParts = part.split(/([:：])/).filter(Boolean);
      subParts.forEach((sub, subIndex) => {
        const isColon = /^[:：]$/.test(sub);
        segments.push({
          text: sub,
          isNum: true,
          isAfterAp: subIndex === 0 && isAfterAp,
          isClockHour: subIndex === 0 && !isColon,
          isClockColon: isColon,
          isClockMinute: subIndex > 0 && !isColon,
        });
      });
      return;
    }
    segments.push({
      text: part,
      isNum,
      isAfterAp,
      isClockHour: false,
      isClockColon: false,
      isClockMinute: false,
    });
  });
  return segments;
};

const isHuawei = computed(() => {
  const m = props.appearance?.model || useSystemStore.appearance?.model;
  return m === 'huawei_junxiu';
});

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

// 判断是否为无头像的中间提示类“字条”（时间、撤回、拍一拍、系统消息）
const isNoticeType = (type) => ['time', 'takeAPat', 'revoke', 'system'].includes(type);

const isTimeAfterRevoke = (index) => {
  if (index <= 0) return false;
  return useChatStore.chatList[index]?.type === 'time' && useChatStore.chatList[index - 1]?.type === 'revoke';
};

const isTimeBeforeRevoke = (index) => {
  if (index >= useChatStore.chatList.length - 1) return false;
  return useChatStore.chatList[index]?.type === 'time' && useChatStore.chatList[index + 1]?.type === 'revoke';
};

const isRevokeAfterTime = (index) => {
  if (index <= 0) return false;
  return useChatStore.chatList[index]?.type === 'revoke' && useChatStore.chatList[index - 1]?.type === 'time';
};

const isTimeAfterNotice = (index) => {
  if (index <= 0) return false;
  return useChatStore.chatList[index]?.type === 'time' && isNoticeType(useChatStore.chatList[index - 1]?.type);
};

const isTimeBeforeNotice = (index) => {
  if (index >= useChatStore.chatList.length - 1) return false;
  return useChatStore.chatList[index]?.type === 'time' && isNoticeType(useChatStore.chatList[index + 1]?.type);
};

const isNoticeAfterTime = (index) => {
  if (index <= 0) return false;
  const curr = useChatStore.chatList[index]?.type;
  return isNoticeType(curr) && curr !== 'time' && useChatStore.chatList[index - 1]?.type === 'time';
};

const isNoticeAfterNotice = (index) => {
  if (index <= 0) return false;
  return isNoticeType(useChatStore.chatList[index]?.type) && isNoticeType(useChatStore.chatList[index - 1]?.type);
};

const voiceWidth = (chat) => {
  const duration = Math.min(60, Math.max(1, Math.round(Number(chat.duration) || 1)));
  let segments = 0;
  if (duration <= 10) {
    segments = duration - 1;
  } else {
    // 11~19和10一样长，20~29加一段，30~39加一段，40~49加一段，50~59加一段，60加最后一段
    segments = 8 + Math.floor(duration / 10);
  }
  const totalSegments = 14;

  // 根据当前机型宽度按比例计算语音气泡长度（基准：默认机型 1080px 下 min:203px, max:550px）
  // 华为机型宽度为 1256px，比例为 1256 / 1080 ≈ 1.163，对应 min:236px, max:640px
  const modelWidth = isHuawei.value ? 1256 : (props.appearance?.width || useSystemStore.phoneWidth || 1080);
  const scale = modelWidth / 1080;
  const minWidth = 203 * scale;
  const maxWidth = 550 * scale;

  return Math.round(minWidth + segments * ((maxWidth - minWidth) / totalSegments));
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
      padding: var(--phone-item-padding-y, 16px) 36px;
      position: relative;
      display: flex;
      &:hover, &.active {
        background-color: rgba(0, 0, 0, .15);
      }
      .wechat-item-name {
        margin: 0 0 12px var(--phone-username-margin-left, 162px);
        font-size: var(--phone-username-size, 42px);
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
        padding: var(--phone-message-padding-y, 28px) var(--phone-message-padding-x, 38px);
        font-size: var(--phone-message-size, 48px);
        border-radius: 15px;
        margin-right: var(--phone-bubble-margin-far, 140px);
        word-break: break-all;
        margin-left: var(--phone-bubble-margin-near, 133px);
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
          top: 50%;
          margin-top: -12px;
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
            top: var(--phone-message-tail-top, 50px);
            margin-top: 0;
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
            top: var(--phone-message-tail-top, 50px);
            margin-top: 0;
          }
        }
        &.wechat-item-voice {
          display: flex;
          align-items: center;
          padding-left: 23px;
          > span.voice-duration {
            font-family: inherit;
            font-size: var(--phone-message-size, 42px);
            font-weight: inherit;
            line-height: 1;
            padding-right: 20px;
            width: auto;
            min-width: 60px;
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
            .av-label {
              margin-right: 8px;
            }
          }
          i {
            display: block;
            position: relative;
            top: var(--phone-av-icon-top, 2px);
            width: var(--phone-av-icon-width, 50px);
            height: var(--phone-av-icon-height, 21px);
            background-image: url(@/WechatTool/assets/images/content/wechat-audio-light.png);
            background-repeat: no-repeat;
            background-size: contain;
            background-position: center;
            margin: 0 12px 0 0;
            &.video {
              width: var(--phone-av-icon-width, 50px);
              height: calc(var(--phone-av-icon-width, 50px) * 38 / 50);
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
          margin-left: var(--phone-bubble-margin-far, 140px);
          margin-right: var(--phone-bubble-margin-near, 133px);
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
            > span.voice-duration {
              font-family: inherit;
              font-size: var(--phone-message-size, 42px);
              font-weight: inherit;
              line-height: 1;
              padding-left: 20px;
              padding-right: 0;
              text-align: right;
              width: auto;
              min-width: 60px;
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
              .av-label {
                margin-right: 8px;
              }
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
          padding-top: var(--phone-time-padding-top, 38px);
          padding-bottom: var(--phone-time-padding-bottom, 38px);
          &.wechat-item-time-after-revoke,
          &.wechat-item-time-after-notice {
            padding-top: calc(var(--phone-time-padding-top, 38px) - var(--phone-time-after-revoke-reduce, 40px));
          }
          &.wechat-item-time-before-revoke,
          &.wechat-item-time-before-notice {
            padding-bottom: calc(var(--phone-time-padding-bottom, 38px) - var(--phone-time-before-revoke-reduce, 15px));
          }
          .wechat-item-notice {
            font-size: var(--phone-time-size, 32px);
            font-weight: var(--phone-time-weight, 50);
            letter-spacing: var(--phone-time-letter-spacing, 0px);
            .wechat-item-time-content {
              display: inline-block;
              span {
                display: inline;
                transform: none;
                &.time-num-after-ap {
                  margin-left: 10px; /* 上午/下午和右边的时间数字之间的距离增加10px */
                }
              }
            }
          }
        }

        /* 重叠字条（时间戳与撤回/提示条连续出现，或连续两条提示字条紧密重叠） */
        &.wechat-item-revoke-after-time,
        &.wechat-item-notice-after-time {
          margin-top: calc(-1 * var(--phone-revoke-after-time-reduce, 30px));
          padding-top: 0;
        }

        &.wechat-item-notice-after-notice:not(.wechat-item-time-box):not(.wechat-item-notice-after-time) {
          margin-top: -12px;
          padding-top: 4px;
        }

        .wechat-item-notice {
          font-size: 32px;
          font-weight: 50;
          color: #a6a6a6;
          .wechat-item-revoke {
            font-size: var(--phone-revoke-size, 34px);
            font-weight: var(--phone-revoke-weight, 500);
            letter-spacing: var(--phone-revoke-letter-spacing, 0px);
          }
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

  &.huawei-body {
    .wechat-content {
      .wechat-item-name,
      .wechat-item-name * {
        font-family: '『汜霰』有瑶圆', '汜霰有瑶圆', 'SiXianYouYaoYuan', 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
      }

      .wechat-item-notice,
      .wechat-item-revoke,
      .wechat-item-text,
      .wechat-item-text * {
        font-family: 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
      }

      .wechat-item-name {
        position: relative;
        top: -11px; /* 联系人姓名向上移动11px */
        font-weight: 500;
        -webkit-text-stroke: 1.25px currentColor; /* 联系人名字粗细，可调节数值（越大越粗） */
      }

      /* 气泡内字体增粗，可通过 -webkit-text-stroke 标签微调 */
      .wechat-item-text {
        font-weight: 500;
        -webkit-text-stroke: 1px currentColor; /* 在此调整华为气泡内文字粗细标签（数值越大越粗） */
      }

      .wechat-item {
        .wechat-item-text.wechat-item-voice {
          display: flex;
          align-items: center;
          padding-top: 0;
          padding-bottom: 0;

          i {
            width: 35px;
            height: 50px;
            flex: 0 0 35px;
            align-self: center;
            margin-top: 0;
            margin-bottom: 0;
            margin-right: 12px;
            margin-left: 0;
            background-size: 100% 100%;
            background-position: center;
            background-repeat: no-repeat;
          }

          span.voice-duration {
            font-family: inherit;
            font-size: var(--phone-message-size, 51px);
            line-height: 1;
            display: inline-flex;
            align-items: center;
            align-self: center;
            min-width: 0;
            padding: 0;
            margin: 0;

            /* 语音消息中的数字（如 5）及后面符号 " 均减少粗细并增加横向宽度；数字部分字号再减小2px（-9px），并轻微加粗 */
            .voice-num {
              font-family: 'DFPYuanTime-B5', 'DFPYuanBold-B5', 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
              display: inline-block;
              line-height: 1;
              min-width: 0;
              padding: 0;
              margin: 0 2px 0 0;
              font-size: calc(var(--phone-message-size, 51px) - 9px);
              font-weight: 400;
              -webkit-text-stroke: 0.45px currentColor; /* 在此调整语音消息数字粗细标签（0px为细字体，数值越大越粗） */
              transform: scale(1.18, 1); /* 横向加宽 */
              transform-origin: center center;
            }

            .voice-unit {
              font-family: 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
              display: inline-block;
              line-height: 1;
              min-width: 0;
              padding: 0;
              margin: 0 2px 0 4px;
              font-size: calc(var(--phone-message-size, 51px) - 9px);
              font-weight: 280;
              -webkit-text-stroke: 0px currentColor; /* 跟随数字减少粗细 */
              transform: scale(1.18, 1); /* 跟随数字增加横向宽度 */
              transform-origin: center center;
            }
          }

          em {
            top: 50%;
            transform: translateY(-50%);
          }
        }

        .wechat-item-text.wechat-item-av {
          display: flex;
          align-items: center;
          padding: 0 43px;

          i:not(.video) {
            width: 60px;
            height: calc(60px * 51 / 117);
            flex: 0 0 60px;
            background-image: url(@/WechatTool/assets/images/content/huawei-audio-light.svg);
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            align-self: center;
            top: 0;
            margin: 0;
          }

          span {
            display: inline-flex;
            align-items: center;
            line-height: 1;
            align-self: center;
            margin: 0 0 0 12px; /* 对方语音通话：通话图标与后面的文字之间的距离减少10px（原16px，现6px） */

            .av-label {
              display: inline-flex;
              align-items: center;
              line-height: 1;
              margin-right: 6px; /* 对方语音通话：数字部分距离前面文字（通话时长）减小6px（原12px，现6px） */
            }

            /* 语音通话中的数字与符号（如 00:10）使用减细版 DFPYuanTime-B5 字体，字号再减小2px（-4px），轻微加粗并垂直居中、横向加宽 */
            .av-num {
              font-family: 'DFPYuanTime-B5', 'DFPYuanBold-B5', 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
              position: relative;
              top: 0; /* 去除原先向下偏移，确保与“通话时长”及图标垂直居中 */
              display: inline-flex;
              align-items: center;
              line-height: 1;
              font-size: calc(var(--phone-message-size, 51px) - 4px);
              font-weight: 400;
              -webkit-text-stroke: 0.45px currentColor; /* 在此调整语音通话数字及符号粗细标签（0px为细字体，数值越大越粗） */
              transform: scale(1.18, 1); /* 增加横向宽度 */
              transform-origin: center center;
              margin: 0 10px;
            }
          }
        }

        &.wechat-item-right {
          .wechat-item-text.wechat-item-voice {
            flex-direction: row-reverse;
            padding-left: 43px;
            padding-right: 43px;
            i {
              width: 35px;
              height: 50px;
              flex: 0 0 35px;
              align-self: center;
              margin-top: 0;
              margin-bottom: 0;
              margin-left: 10px; /* 数字和秒数整体往右侧头像侧贴近（消除原内层span额外间距并缩紧至10px） */
              margin-right: 0;
            }
            span.voice-duration {
              padding: 0;
              min-width: 0;
              .voice-num {
                padding: 0;
                margin: 0 2px 0 0;
                min-width: 0;
              }
              .voice-unit {
                padding: 0;
                margin: 0 2px 0 4px;
                min-width: 0;
              }
            }
          }
          .wechat-item-text.wechat-item-av {
            flex-direction: row-reverse;
            padding-left: 43px;
            padding-right: 43px;
            span {
              margin: 0 8px 0 0; /* 时长与语音通话图标之间的距离减少8px（原16px，减少8px后为8px） */

              .av-label {
                margin-right: 20px; /* 在此调整“语音通话”字（通话时长）与时长之间的距离（增加20px） */
              }
            }
            i:not(.video) {
              margin: 0;
            }
          }
        }
      }

      &.dark {
        .wechat-item:not(.wechat-item-right) {
          .wechat-item-text.wechat-item-av {
            i:not(.video) {
              background-image: url(@/WechatTool/assets/images/content/huawei-audio-dark.svg);
            }
          }
        }
        .wechat-item.wechat-item-right {
          .wechat-item-text.wechat-item-av {
            i:not(.video) {
              background-image: url(@/WechatTool/assets/images/content/huawei-audio-light.svg);
            }
          }
        }
      }

      .wechat-item-time-box {
        .wechat-item-notice {
          font-family: 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;

          .wechat-item-time-content {
            display: inline-block;
            transform: none; /* 取消父级 .wechat-item-notice span 的 scaleX(0.95) 缩放，避免抵消数字横向加宽 */

            /* 文字部分（如：昨天、上午、下午、年、月、日等）—— 增大2px字体，比现在粗，可通过修改 -webkit-text-stroke 标签调节具体粗细 */
            .time-text {
              display: inline;
              font-family: inherit;
              font-size: calc(var(--phone-time-size, 33px) + 2px); /* 文字部分增大2px字体 */
              font-weight: 300;
              -webkit-text-stroke: 0.3px currentColor; /* 在此调整时间戳【文字】粗细标签（数值越大越粗） */
            }

            /* 数字部分（如：12:30、2024等）—— 使用减细版 DFPYuanTime-B5 字体（改细一点点），并横向加宽 */
            .time-num {
              display: inline-block !important;
              font-family: 'DFPYuanTime-B5', 'DFPYuanBold-B5', 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
              font-size: var(--phone-time-size, 33px);
              letter-spacing: 0px; /* 数字之间的间隔减少2px（原2px，现0px） */
              font-weight: 400;
              -webkit-text-stroke: 0px currentColor; /* 在此调整时间戳【数字】粗细标签（0px为细字体，数值越大越粗） */
              transform: scale(1.18, 1) !important; /* 数字直接调控横向加宽：scale(X横向加宽, Y纵向缩放) */
              transform-origin: center baseline;
              vertical-align: baseline;
              margin: 0 3px;

              /* 上午/下午和右边时钟时间之间的距离再增加4px */
              &.time-num-after-ap {
                margin-left: 14px;
              }

              /* 时钟小时、冒号、分钟之间的距离各收紧8px（消除宽冒号留白） */
              &.time-num-hour {
                margin-right: 0;
              }

              &.time-num-colon {
                margin-left: 0px;
                margin-right: 2px;
              }

              &.time-num-minute {
                margin-left: 0;
              }
            }
          }
        }
      }

      /* 华为机型重叠字条紧凑样式（时间戳、撤回、拍一拍等连续字条） */
      .wechat-item-notice-box {
        &.wechat-item-revoke-after-time,
        &.wechat-item-notice-after-time {
          margin-top: -30px; /* 撤回/提示字条在时间戳后向上贴近重叠 */
          padding-top: 0;
        }
        &.wechat-item-time-after-revoke,
        &.wechat-item-time-after-notice {
          padding-top: calc(var(--phone-time-padding-top, 87px) - var(--phone-time-after-revoke-reduce, 40px));
        }
        &.wechat-item-time-before-revoke,
        &.wechat-item-time-before-notice {
          padding-bottom: calc(var(--phone-time-padding-bottom, 62px) - var(--phone-time-before-revoke-reduce, 15px));
        }
        &.wechat-item-notice-after-notice:not(.wechat-item-time-box):not(.wechat-item-notice-after-time) {
          margin-top: -16px; /* 连续提示字条向上重叠 */
          padding-top: 4px;
        }

        .wechat-item-notice {
          .wechat-item-revoke {
            font-family: 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
            font-weight: 500;
            -webkit-text-stroke: 0.5px currentColor;
          }
        }
      }

      .wechat-item-revoke {
        font-family: 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
        font-weight: 500;
        -webkit-text-stroke: 0.1px currentColor;
      }
    }
  }
}
</style>