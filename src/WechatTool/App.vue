<template>
  <a-config-provider :theme="{
    token: {
      colorPrimary: '#888888',
    },
  }" :locale="zhCN">
    <a-layout @click="handleAppClick" @contextmenu="handleAppContextMenu">
      <a-layout-header :style="headerStyle">
        <WtHeader />
      </a-layout-header>
      <a-layout class="content" v-if="!isPhone">
        <!-- <a-layout-sider :style="siderStyle" :width="useSystemStore.activeMenu === 'chat' ? 640 : 480"> -->
        <a-layout-sider :style="siderStyle" :width="640">
          <WtSider />
        </a-layout-sider>
        <a-layout-content>
          <Suspense>
            <template #default>
              <WtContent />
            </template>
            <template #fallback>
              <div class="default-loading">
                <a-spin tip="加载中..."></a-spin>
              </div>
            </template>
          </Suspense>
        </a-layout-content>
      </a-layout>
      <a-layout class="content" v-else>
        <IsPhone />
      </a-layout>
    </a-layout>
  </a-config-provider>

  <ContextMenu />
</template>

<script setup>
import { onMounted, onUnmounted, ref, defineAsyncComponent } from 'vue';
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
dayjs.locale('zh-cn');
import WtHeader from "@/WechatTool/components/WtHeader.vue"
import WtSider from "@/WechatTool/components/WtSider.vue"
// import WtContent from "@/WechatTool/components/WtContent.vue"
const WtContent = defineAsyncComponent(() => import('@/WechatTool/components/WtContent.vue'));
import Instructions from "@/WechatTool/components/common/Instructions.vue"
import ContextMenu from "@/WechatTool/components/common/ContextMenu.vue"
import IsPhone from "@/WechatTool/components/common/IsPhone.vue"
import useStore from "@/WechatTool/store";
const { useSystemStore, useUserStore, useChatStore, useContextMenuStore } = useStore();
import { ownAvatar, otherAvatar } from "@/WechatTool/utils/avatar";

const headerStyle = {
  height: '50px',
  lineHeight: '50px',
  paddingInline: 0,
  backgroundColor: 'var(--bg-color)',
};

const siderStyle = {
  paddingInline: 0,
  backgroundColor: 'var(--bg-color)',
};



const showFork = ref(false);
onMounted(() => {
  showFork.value = process.env.NODE_ENV !== "development";
  // 在这里初始化数据
  if (!useUserStore.userList.length) {
    useUserStore.userList = [
      {
        id: "user-0",
        nickname: "你自己",
        avatar: ownAvatar,
        role: "own",
      },
      {
        id: "user-" + Date.now(),
        nickname: "小甜甜",
        avatar: otherAvatar,
        role: "other",
      }
    ]
    useUserStore.activeUserId = useUserStore.userList[0]['id'];
  }
  if (!useChatStore.chatList.length) {
    useChatStore.chatList = [
      {
        id: "chat-1",
        type: "text",
        content: "你是谁",
        user: useUserStore.userList[0],
        role: "own",
      },
      {
        id: "chat-2",
        type: "text",
        content: "我是小甜甜~",
        user: useUserStore.userList[1],
        role: "other",
      }
    ]
  }
  handleResize();
  window.addEventListener('resize', handleResize);
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
})

const handleAppClick = () => {
  useContextMenuStore.hideContextMenu();
  useContextMenuStore.activeChatId = "";
}
const handleAppContextMenu = (e) => {
  useContextMenuStore.hideContextMenu();
  useContextMenuStore.activeChatId = "";
}

const isPhone = ref(false);
const handleResize = () => {
  isPhone.value = window.innerWidth <= 640;
}
</script>

<style lang="less" scoped>
@import url(//at.alicdn.com/t/c/font_4238507_is5sbfgeqfc.css);
.content {
  height: calc(100vh - 50px);
  background-color: var(--bg-color);
}
.widget {
  position: fixed;
  top: 0;
  right: 0;
}
</style>
