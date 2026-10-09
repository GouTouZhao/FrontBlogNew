import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

import pinia from "@/WechatTool/store/pinia";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css";
import "@/WechatTool/global.less";

import { PerfectScrollbarPlugin } from 'vue3-perfect-scrollbar'
import 'vue3-perfect-scrollbar/style.css'

const app = createApp(App)

app.use(pinia)
app.use(Antd)
app.use(PerfectScrollbarPlugin, {
  watchOptions: true,
  options: {
    minScrollbarLength: 38,
  }
})

app.use(router)
app.mount('#app')
