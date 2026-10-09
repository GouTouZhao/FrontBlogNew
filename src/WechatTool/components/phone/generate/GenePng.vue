<template>
  <a-tooltip title="滚动到哪截到哪" placement="right">
    <div class="wtc-button" @click="handleGeneratePng">生成图片</div>
  </a-tooltip>
  <a-tooltip title="顾名思义" placement="right">
    <div class="wtc-button" @click="handleGenerateLongPng">生成长图</div>
  </a-tooltip>

  <a-drawer :width="500" :title="drawerTitle" placement="right" :closable="false" :destroyOnClose="true" :open="drawerVisible" @close="onClose">
    <template #extra>
      <a-space>
        <a-button type="primary" :disabled="!imageUrl" @click="handleDownload">下载</a-button>
        <a-button danger type="link" shape="circle" :icon="h(CloseOutlined)" :disabled="!imageUrl" @click="onClose" />
      </a-space>
    </template>
    <img :src="imageUrl" alt="">
  </a-drawer>
</template>

<script setup>
import { ref, h } from "vue";
import { CloseOutlined } from '@ant-design/icons-vue';
import dayjs from "dayjs";
import { useHtmlToImage } from '@/WechatTool/hooks/useHtmlToImage';
import useStore from "@/WechatTool/store";
const { imageUrl, captureHtmlToImage } = useHtmlToImage();
const { useSystemStore } = useStore();

const drawerVisible = ref(false);
const drawerTitle = ref('');

// 生成图片
const handleGeneratePng = async () => {
  const phone = document.querySelector('#phone');
  await captureHtmlToImage(phone, {
    width: useSystemStore.phoneWidth,
    height: useSystemStore.phoneHeight,
  });
  drawerVisible.value = true;
  drawerTitle.value = "生成图片";
}

// 生成长图
const handleGenerateLongPng = async () => {
  const wechatContent = document.querySelector('.wechat-content')
  const phoneBg = document.querySelector('.phone-bg')
  const chatBackground = useSystemStore.appearance.chatBackground
  const phone = document.querySelector('#phone')
  const phoneBody = document.querySelector('.phone-body')
  const contentTop = Number.parseInt(getComputedStyle(phone).getPropertyValue('--phone-content-top')) || 264;
  const contentBottom = Number.parseInt(getComputedStyle(phone).getPropertyValue('--phone-content-bottom')) || 269;
  const phoneRealHeight = useSystemStore.phoneHeight > wechatContent.scrollHeight + contentTop + contentBottom ? useSystemStore.phoneHeight : wechatContent.scrollHeight + contentTop + contentBottom;
  phone.style.height = phoneRealHeight + "px"
  phoneBody.scrollTop = 0
  if (chatBackground) {
    phoneBody.style.background = `url(${chatBackground}) repeat-y center top`
    phoneBody.style.backgroundSize = `${useSystemStore.phoneWidth}px auto`
    phoneBg.querySelector('img').setAttribute('src', '')
  }

  await captureHtmlToImage(phone, {
    width: useSystemStore.phoneWidth,
    height: phoneRealHeight,
  });

  phone.style.height = useSystemStore.phoneHeight + "px";
  if (chatBackground) {
    phoneBg.querySelector('img').setAttribute('src', chatBackground)
    phoneBody.style.background = ""
  }
  drawerVisible.value = true;
  drawerTitle.value = "生成长图";
}

const onClose = () => {
  drawerVisible.value = false;
  imageUrl.value = "";
}

const handleDownload = () => {
  const link = document.createElement('a');
  link.href = imageUrl.value;
  link.download = `微信聊天图片 - ${dayjs().format('YYYYMMDDHHmmss')}.png`;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
</script>