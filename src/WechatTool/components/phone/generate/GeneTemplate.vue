<template>
  <a-tooltip title="将当前对话复制为文字模板" placement="right">
    <div class="wtc-button" @click="handleSaveTemplate">复制模板文字</div>
  </a-tooltip>
  <a-tooltip title="导出聊天为文本文件" placement="right">
    <div class="wtc-button" @click="handleExportChat">导出聊天</div>
  </a-tooltip>
  <a-tooltip title="导入聊天内容（支持直接粘贴或读取文件）" placement="right">
    <div class="wtc-button" @click="openImportModal">导入聊天</div>
  </a-tooltip>

  <!-- 导入聊天内容弹窗 -->
  <a-modal
    v-model:open="importModalVisible"
    title="导入聊天内容"
    width="680px"
    okText="确认导入"
    cancelText="取消"
    @ok="handleConfirmImport"
  >
    <div class="import-modal-wrap">
      <div class="import-modal-desc">
        请在下方输入框中<strong>直接粘贴聊天文本</strong>，系统将自动解析对话及顶部机型/时间/电量等设置并写入预览；也可以选择读取本地文件。
      </div>
      <div class="import-modal-actions">
        <label class="import-file-btn">
          选择文件读取
          <input type="file" accept=".txt,.json" hidden @change="handleFileSelected" />
        </label>
        <a-button size="small" @click="importTextContent = ''">清空内容</a-button>
        <a-button size="small" type="link" @click="handleFillSample">填入示例模板</a-button>
      </div>
      <a-textarea
        v-model:value="importTextContent"
        :rows="12"
        placeholder="请在此粘贴聊天文本内容，例如：&#10;机型：华为细圆&#10;手机时间：12:30&#10;手机电量：80%&#10;对方用户名：派大星&#10;&#10;文本：我：你好派大星。&#10;文本：对方：你好GouTou！&#10;语音：对方：5秒&#10;通话：我：通话时长 00:10"
      />
    </div>
  </a-modal>
</template>

<script setup>
import { ref } from "vue";
import dayjs from "dayjs";
import FileSaver from 'file-saver';
import useStore from "@/WechatTool/store";
import { toast } from "@/WechatTool/utils/feedback";
import { chatListToText, textToChatList } from "@/WechatTool/utils/chatTextAdapter";

const { useChatStore, useUserStore, useSystemStore } = useStore();

const importModalVisible = ref(false);
const importTextContent = ref("");

const openImportModal = () => {
  importModalVisible.value = true;
};

const handleSaveTemplate = async () => {
  const exportText = chatListToText(useChatStore.chatList, {
    systemStore: useSystemStore,
    userStore: useUserStore,
  });
  try {
    await navigator.clipboard.writeText(exportText);
    toast({ type: "success", content: "模板文字已复制到剪贴板，请自行保存" });
  } catch (err) {
    const input = document.createElement("textarea");
    input.value = exportText;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    document.body.removeChild(input);
    toast({ type: "success", content: "模板文字已复制到剪贴板，请自行保存" });
  }
};

const handleExportChat = () => {
  const exportText = chatListToText(useChatStore.chatList, {
    systemStore: useSystemStore,
    userStore: useUserStore,
  });
  const blob = new Blob([exportText], {
    type: 'text/plain;charset=utf-8'
  });
  FileSaver.saveAs(blob, `聊天记录 - ${dayjs().format('YYYYMMDDHHmmss')}.txt`);
};

const handleFileSelected = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.readAsText(file);
  reader.onload = (res) => {
    try {
      importTextContent.value = res.target.result || "";
      toast({ type: "success", content: `已读取文件内容，请核对后点击确认导入` });
    } catch (err) {
      toast({ type: "error", content: "文件读取失败" });
    } finally {
      e.target.value = "";
    }
  };
};

const handleFillSample = () => {
  importTextContent.value = `机型：华为细圆
手机时间：12:30
手机电量：80%
对方用户名：派大星

文本：我：你好派大星。
文本：对方：你好GouTou！
语音：对方：5秒
通话：我：通话时长 00:10
文本：对方：好的，稍后联系。`;
};

const handleConfirmImport = () => {
  if (!importTextContent.value || !importTextContent.value.trim()) {
    toast({ type: "warning", content: "请先粘贴或输入聊天内容" });
    return;
  }
  try {
    const chatList = textToChatList(importTextContent.value, {
      userStore: useUserStore,
      systemStore: useSystemStore,
    });
    if (chatList && chatList.length) {
      useChatStore.chatList = chatList;
      importModalVisible.value = false;
      toast({
        type: "success",
        content: `成功导入 ${chatList.length} 条聊天记录并已写入预览`,
      });
    } else {
      toast({
        type: "warning",
        content: "内容中未识别到有效聊天记录，请检查格式后重试",
      });
    }
  } catch (err) {
    toast({
      type: "error",
      content: "导入解析失败，请检查内容格式",
    });
  }
};
</script>

<style lang="less" scoped>
.import-modal-wrap {
  .import-modal-desc {
    font-size: 13px;
    color: #666;
    margin-bottom: 12px;
    line-height: 1.6;
  }

  .import-modal-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;

    .import-file-btn {
      display: inline-block;
      padding: 3px 12px;
      font-size: 13px;
      background: #1890ff;
      color: #fff;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #40a9ff;
      }
    }
  }
}
</style>