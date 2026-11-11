import { defineStore } from "pinia";
import _ from "lodash";
const appearance = {
  model: "huawei_junxiu",
  darkMode: false,
  networkType: "default",
  wifiSignal: "default",
  phoneSignal: "default",
  phoneSignal2: "default",
  phoneTimeHour: "12",
  phoneTimeMinute: "21",
  timeFollowSystem: true,
  isCharging: false,
  phoneBattery: 60,
  earphoneMode: false,
  unreadMessages: 0,
  chatTitle: "派大星",
  showChatName: false,
  voiceMode: false,
  syncInputText: true,
  chatBackground: "",
}

export const useSystemStore = defineStore("toolSystem", {
  state: () => {
    return {
      activeMenu: "appearance", // 当前聚焦的工具栏目
      appearance: _.cloneDeep(appearance),
      phoneWidth: 1256,
      phoneHeight: 2760,
      phoneScale: 360 / 1256,
      hadDisclaimer: false, // 已经确认过声明
      qqGroupLink: "http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=FBr4JIxIckrUqgDK-rbdMkoQYfJT4BCs&authKey=Dl1dUP8%2BXRNefHTYG38DyEi3CAOf20Pc8yyIJwKQ7HlP5WX7nYhURs2vVtmttNHX&noverify=0&group_code=887911914", // 跳转加群链接
    };
  },
  actions: {
    resetAppearance() {
      this.appearance = _.cloneDeep(appearance)
    },
  },
  persist: {
    enabled: true,
    strategies: [
      {
        storage: localStorage,
      },
    ],
  },
});
