<template>
  <div class="wt-sider" :class="{ 'batch-sider-collapsed': useSystemStore.activeMenu === 'batch' }">
    <div class="menu-box">
      <div v-for="menu in menus" :key="menu.value" class="menu-item"
        :class="{ active: useSystemStore.activeMenu === menu.value }" @click="handleMenuClick(menu)">
        <component :is="menuIcons[menu.value]" class="menu-icon" />
        <p>{{ menu.label }}</p>
      </div>
    </div>
    <div class="wt-config" v-if="useSystemStore.activeMenu !== 'batch'">
      <keep-alive>
        <component :is="configComponents[useSystemStore.activeMenu]" />
      </keep-alive>
    </div>
  </div>
</template>

<script setup>
import { reactive, shallowRef } from "vue";
import {
  SettingOutlined,
  MessageOutlined,
  AppstoreAddOutlined,
  QuestionCircleOutlined,
} from "@ant-design/icons-vue";
import ConfigAppearance from "./ConfigAppearance.vue";
import ConfigChat from "./ConfigChat.vue";
import ConfigInstructions from "./ConfigInstructions.vue";
import useStore from "@/WechatTool/store";
const { useSystemStore } = useStore();

const menus = reactive([
  {
    label: "外观设置",
    value: "appearance",
  }, {
    label: "对话设置",
    value: "chat",
  }, {
    label: "批量生成",
    value: "batch",
  }, {
    label: "使用说明",
    value: "instructions",
  }
]);

const menuIcons = {
  appearance: SettingOutlined,
  chat: MessageOutlined,
  batch: AppstoreAddOutlined,
  instructions: QuestionCircleOutlined,
};

const handleMenuClick = (menu) => {
  useSystemStore.activeMenu = menu.value;
};

const configComponents = shallowRef({
  appearance: ConfigAppearance,
  chat: ConfigChat,
  instructions: ConfigInstructions,
});
</script>

<style lang="less" scoped>
.wt-sider {
  display: flex;
  height: 100%;

  &.batch-sider-collapsed {
    width: 80px;
  }

  .menu-box {
    width: 80px;
    height: 100%;
    background-color: var(--border-color);

    .menu-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 80px;
      cursor: pointer;
      transition: all .3s;
      color: gray;
      opacity: 0.8;

      .menu-icon,
      i {
        font-size: 24px;
        margin-bottom: 6px;
      }

      &.active {
        background-color: var(--bg-color);
        opacity: 1;
        color: var(--text-color);
        font-weight: bold;
      }
      &:hover {
        background-color: var(--bg-color);
        opacity: 0.9;
        color: var(--text-color);
      }
      p {
        margin: 0;
      }
    }
  }
}
.wt-config {
  width: calc(100% - 80px);
  flex: 1;
  padding: 20px;
  background-color: var(--bg-color);
  color: var(--text-color);
}
</style>