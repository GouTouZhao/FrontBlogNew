<template>
  <div class="phone-nav" :class="{'dark': appearance.darkMode, 'huawei-nav': isHuawei}">
    <div class="phone-nav-left">
      <div class="phone-nav-back">返回</div>
      <span v-if="appearance.unreadMessages">{{appearance.unreadMessages > 99 ? '99+' : appearance.unreadMessages}}</span>
    </div>
    <div class="phone-nav-center">
      <span class="center-span"> <span class="user-name">{{chatTitle}}</span> <i v-if="appearance.earphoneMode"></i> </span>
    </div>
    <div class="phone-nav-right">
      <div class="phone-nav-more">更多</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import useStore from "@/WechatTool/store";
const { useSystemStore } = useStore();
import { truncateMiddle } from "@/WechatTool/utils/utils"

const props = defineProps({
  appearance: {
    type: Object,
    default: () => {},
  }
})

const isHuawei = computed(() => {
  const m = props.appearance?.model || useSystemStore.appearance?.model;
  return m === 'huawei_junxiu';
});

const chatTitle = computed(() => {
  return truncateMiddle(useSystemStore.appearance.chatTitle, 14)
})
</script>

<style lang="less" scoped>
.phone-nav {
  height: var(--phone-nav-height, 132px);
  position: relative;
  z-index: 99999;
  display: flex;
  align-items: center;
  padding: 0 50px;
  .phone-nav-left {
    width: 150px;
    position: relative;

    .phone-nav-back {
      width: 27px;
      height: 52px;
      background: url(@/WechatTool/assets/images/nav/wechat-nav-back-light.png) no-repeat;
      text-indent: -9999px;
    }

    span {
      position: absolute;
      font-size: 36px;
      height: 72px;
      line-height: 72px;
      background: #d5d5d5;
      min-width: 72px;
      border-radius: 36px;
      text-align: center;
      padding: 0 24px;
      top: 50%;
      margin-top: -36px;
      left: 45px;
      font-weight: 600;
    }
  }

  .phone-nav-center {
    flex: 1;
    display: flex;
    justify-content: center;
    .center-span {
      font-size: var(--phone-nav-title-size, 42px);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: var(--phone-nav-title-weight, 500);
      -webkit-text-stroke: 0.5px currentColor; /* 微调文字粗细，可以修改 0.5px 来调节 */
      letter-spacing: 3px; /* 微调字间距 */
      .user-name {
        font-family: inherit;
        font-size: inherit;
        font-weight: inherit;
        -webkit-text-stroke: inherit;
        letter-spacing: inherit;
      }
      i {
        width: var(--phone-nav-earphone-width, 36px);
        height: var(--phone-nav-earphone-height, 44px);
        background: url(@/WechatTool/assets/images/nav/wechat-trans-earphone-light.png) no-repeat;
        background-size: 100% 100%;
        margin: var(--phone-nav-earphone-margin-top, 8px) 0 0 15px;
      }
    }
  }

  &.huawei-nav {
    .phone-nav-center {
      .center-span,
      .center-span * {
        font-family: '『汜霰』有瑶圆', '汜霰有瑶圆', 'SiXianYouYaoYuan', 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif !important;
      }
      .center-span {
        font-weight: 600;
        -webkit-text-stroke: 1.2px currentColor; /* 联系人名字粗细，可调节数值（越大越粗） */
        letter-spacing: 1px;
        transform: translateY(-11px); /* 联系人姓名向上移动11px */
      }
    }
  }

  .phone-nav-right {
    width: 150px;
    display: flex;
    justify-content: flex-end;
    .phone-nav-more {
      width: 70px;
      height: 12px;
      background: url(@/WechatTool/assets/images/nav/wechat-nav-right-light.png) no-repeat;
      text-indent: -9999px;
    }
  }

  &::after {
    content: "";
    position: absolute;
    width: 100%;
    height: 0.67px;
    background: #a0a0a0;
    overflow: hidden;
    left: 0;
    bottom: 2px;
  }

  &.dark {
    .phone-nav-back {
      background: url(@/WechatTool/assets/images/nav/wechat-nav-back-dark.png) no-repeat;
    }
    .phone-nav-center {
      .center-span {
        i {
          background: url(@/WechatTool/assets/images/nav/wechat-trans-earphone-dark.png) no-repeat;
        }
      }
    }
    .phone-nav-right {
      .phone-nav-more {
        background: url(@/WechatTool/assets/images/nav/wechat-nav-right-dark.png) no-repeat;
      }
    }
  }
}
</style>
