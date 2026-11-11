<template>
  <div class="config-template">
    <a-divider style="margin-top: 0;">导出文字模板</a-divider>
    <div style="margin-bottom: 10px;">
      <a-button type="primary" @click="handleExportText">生成文字模板</a-button>
    </div>
    <a-textarea v-model:value="exportText" :rows="6" readonly placeholder="点击上方按钮生成纯文本聊天模板" />
    <div style="margin-top: 10px; text-align: right;" v-if="exportText">
      <a-button type="primary" @click="copyText">复制到剪贴板</a-button>
    </div>

    <a-divider>读取文字模板</a-divider>
    <a-textarea v-model:value="importText" :rows="6" placeholder="请在此处粘贴文字模板，例：&#10;机型：华为细圆&#10;手机时间：12:30&#10;手机电量：80%&#10;对方用户名：派大星&#10;&#10;文本：我：你好派大星。&#10;文本：对方：你好GouTou！&#10;语音：对方：5秒&#10;通话：我：通话时长 00:10" />
    <div style="margin-top: 10px; text-align: right;">
      <a-button type="primary" @click="handleImportText">应用模板</a-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import useStore from "@/WechatTool/store";
import { toast } from "@/WechatTool/utils/feedback";
import { chatListToText, textToChatList } from "@/WechatTool/utils/chatTextAdapter";

const { useChatStore, useUserStore, useSystemStore } = useStore();

const exportText = ref("");
const importText = ref("");

const handleExportText = () => {
  exportText.value = chatListToText(useChatStore.chatList, {
    systemStore: useSystemStore,
    userStore: useUserStore,
  });
  toast({ type: "success", content: "生成成功，请复制保存" });
};

const copyText = async () => {
  try {
    await navigator.clipboard.writeText(exportText.value);
    toast({ type: "success", content: "复制成功" });
  } catch (err) {
    const input = document.createElement("textarea");
    input.value = exportText.value;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    document.body.removeChild(input);
    toast({ type: "success", content: "复制成功" });
  }
};

const handleImportText = () => {
  if (!importText.value) {
    toast({ type: "warning", content: "请先粘贴模板代码" });
    return;
  }
  try {
    const list = textToChatList(importText.value, {
      userStore: useUserStore,
      systemStore: useSystemStore,
    });
    if (Array.isArray(list) && list.length) {
      useChatStore.chatList = list;
      toast({ type: "success", content: `模板应用成功，已写入 ${list.length} 条消息` });
      importText.value = "";
    } else {
      throw new Error("Invalid format");
    }
  } catch (e) {
    toast({ type: "error", content: "解析失败，请检查模板格式" });
  }
};
</script>

<style lang="less" scoped>
.config-template {
  height: 100%;
  overflow-y: auto;
  padding: 10px;
}
</style>