<template>
  <div class="phone-bar" :class="{dark: appearance.darkMode}">
    <!-- 左侧时间 -->
    <div v-if="isHuawei" class="huawei-time-box">
      <div class="phone-time">{{ huaweiPhoneTimeHour }}:{{ appearance.phoneTimeMinute }}</div>
    </div>
    <div v-else class="phone-time">{{ appearance.phoneTimeHour }}:{{ appearance.phoneTimeMinute }}</div>

    <!-- 华为护眼模式图标 (固定距离左侧518px) -->
    <div v-if="isHuawei" class="huawei-icon eye">
      <svg :viewBox="huaweiIcons.eye.viewBox" width="100%" height="100%" fill="currentColor" aria-label="护眼模式">
        <path v-for="(p, i) in huaweiIcons.eye.paths" :key="i" :d="p.d" :transform="p.transform" />
      </svg>
    </div>

    <!-- 右侧状态栏图标 -->
    <div class="phone-status-icons" :class="{'huawei-bar': isHuawei}">
      <!-- 华为俊秀专属状态栏图标 (严格模仿原型) -->
      <template v-if="isHuawei">
        <!-- 1. 闹钟 (基于 VTracer 矢量精准复刻) -->
        <div class="huawei-icon alarm">
          <svg :viewBox="huaweiIcons.alarm.viewBox" width="100%" height="100%" fill="currentColor" aria-label="闹钟">
            <path v-for="(p, i) in huaweiIcons.alarm.paths" :key="i" :d="p.d" :transform="p.transform" />
          </svg>
        </div>

        <!-- 2. 蓝牙 (基于 VTracer 矢量精准复刻) -->
        <div class="huawei-icon bluetooth">
          <svg :viewBox="huaweiIcons.bluetooth.viewBox" width="100%" height="100%" fill="currentColor" aria-label="蓝牙">
            <path v-for="(p, i) in huaweiIcons.bluetooth.paths" :key="i" :d="p.d" :transform="p.transform" />
          </svg>
        </div>

        <!-- 3. 静音 (基于 VTracer 矢量精准复刻) -->
        <div class="huawei-icon mute">
          <svg :viewBox="huaweiIcons.mute.viewBox" width="100%" height="100%" fill="currentColor" aria-label="静音">
            <path v-for="(p, i) in huaweiIcons.mute.paths" :key="i" :d="p.d" :transform="p.transform" />
          </svg>
        </div>

        <!-- 4. Wi-Fi (基于 VTracer 矢量精准复刻，支持信号格数控制与随机机制) -->
        <div class="huawei-icon wifi">
          <svg :viewBox="huaweiIcons.wifi.viewBox" width="100%" height="100%" aria-label="Wi-Fi">
            <path
              v-for="(p, i) in huaweiIcons.wifi.paths"
              :key="i"
              :d="p.d"
              :transform="p.transform"
              :fill="getWifiPathFill(i)"
            />
          </svg>
        </div>

        <!-- 5. 移动网络信号 1 (5 根圆角竖柱条，支持1-5格控制与独立随机) -->
        <div class="huawei-icon mobile-signal first">
          <svg class="huawei-signal-svg" viewBox="0 0 68 55" width="100%" height="100%" aria-label="移动信号1">
            <rect x="0" y="37" width="9.5" height="17" rx="4.75" :fill="phoneSignalLevel1 >= 1 ? 'currentColor' : 'var(--icon-bg)'" />
            <rect x="14.5" y="30" width="9.5" height="24" rx="4.75" :fill="phoneSignalLevel1 >= 2 ? 'currentColor' : 'var(--icon-bg)'" />
            <rect x="29" y="23" width="9.5" height="31" rx="4.75" :fill="phoneSignalLevel1 >= 3 ? 'currentColor' : 'var(--icon-bg)'" />
            <rect x="43.5" y="12" width="9.5" height="42" rx="4.75" :fill="phoneSignalLevel1 >= 4 ? 'currentColor' : 'var(--icon-bg)'" />
            <rect x="58" y="1" width="9.5" height="53" rx="4.75" :fill="phoneSignalLevel1 >= 5 ? 'currentColor' : 'var(--icon-bg)'" />
          </svg>
        </div>

        <!-- 6. 移动网络信号 2 (5 根圆角竖柱条，支持1-5格控制与独立随机) -->
        <div class="huawei-icon mobile-signal second">
          <svg class="huawei-signal-svg" viewBox="0 0 68 55" width="100%" height="100%" aria-label="移动信号2">
            <rect x="0" y="37" width="9.5" height="17" rx="4.75" :fill="phoneSignalLevel2 >= 1 ? 'currentColor' : 'var(--icon-bg)'" />
            <rect x="14.5" y="30" width="9.5" height="24" rx="4.75" :fill="phoneSignalLevel2 >= 2 ? 'currentColor' : 'var(--icon-bg)'" />
            <rect x="29" y="23" width="9.5" height="31" rx="4.75" :fill="phoneSignalLevel2 >= 3 ? 'currentColor' : 'var(--icon-bg)'" />
            <rect x="43.5" y="12" width="9.5" height="42" rx="4.75" :fill="phoneSignalLevel2 >= 4 ? 'currentColor' : 'var(--icon-bg)'" />
            <rect x="58" y="1" width="9.5" height="53" rx="4.75" :fill="phoneSignalLevel2 >= 5 ? 'currentColor' : 'var(--icon-bg)'" />
          </svg>
        </div>

        <!-- 7. 电池 (基于 VTracer 高精矢量复刻华为俊秀电池：外框、电量填充与专有数字) -->
        <div class="huawei-icon battery">
          <!-- 64% 专用高精矢量呈现 (100% 吻合原型图) -->
          <svg
            v-if="batteryDisplay === '64'"
            class="huawei-battery-svg"
            :viewBox="huaweiIcons.battery64.viewBox"
            width="100%"
            height="100%"
            aria-label="电池64%"
          >
            <defs>
              <clipPath id="hw-b64-clip">
                <rect x="135" y="130" width="831" height="448" rx="80" />
              </clipPath>
            </defs>
            <rect
              x="135"
              y="130"
              width="532"
              height="448"
              :fill="appearance.isCharging ? '#22c55e' : 'var(--icon-bg)'"
              clip-path="url(#hw-b64-clip)"
            />
            <g fill="currentColor">
              <path :d="huaweiIcons.battery64.frame.d" :transform="huaweiIcons.battery64.frame.transform" />
              <path :d="huaweiIcons.battery64.tip.d" :transform="huaweiIcons.battery64.tip.transform" />
              <!-- 电池内数字调大3px 并居中 (以中心等比放大并下移居中) -->
              <g transform="translate(550, 380) scale(1.22) translate(-550, -370)">
                <path
                  v-for="(d, i) in huaweiIcons.battery64.digits"
                  :key="i"
                  :d="d.d"
                  :transform="d.transform"
                />
              </g>
            </g>
          </svg>

          <!-- 100% 满电专用高精矢量呈现 (100% 吻合原型图) -->
          <svg
            v-else-if="batteryDisplay === '100'"
            class="huawei-battery-svg"
            :viewBox="huaweiIcons.battery100.viewBox"
            width="100%"
            height="100%"
            aria-label="电池100%"
          >
            <rect
              x="87"
              y="111"
              width="645"
              height="333"
              rx="60"
              :fill="appearance.isCharging ? '#22c55e' : 'var(--icon-bg)'"
            />
            <g fill="currentColor">
              <path :d="huaweiIcons.battery100.frame.d" :transform="huaweiIcons.battery100.frame.transform" />
              <path :d="huaweiIcons.battery100.tip.d" :transform="huaweiIcons.battery100.tip.transform" />
              <!-- 电池内数字调大3px 并居中 (以中心等比放大并下移居中) -->
              <g transform="translate(442, 296) scale(1.22) translate(-442, -288)">
                <path
                  v-for="(d, i) in huaweiIcons.battery100.digits"
                  :key="i"
                  :d="d.d"
                  :transform="d.transform"
                />
              </g>
            </g>
          </svg>

          <!-- 其它动态电量百分比呈现 (基于 VTracer 原型外框 + 动态等比电量填充 + 智能排版) -->
          <svg
            v-else
            class="huawei-battery-svg"
            :viewBox="huaweiIcons.battery64.viewBox"
            width="100%"
            height="100%"
            :aria-label="`电池${batteryDisplay}%`"
          >
            <defs>
              <clipPath id="hw-bdyn-clip">
                <rect x="135" y="130" width="831" height="448" rx="80" />
              </clipPath>
            </defs>
            <rect
              x="135"
              y="130"
              :width="831 * (Number(batteryDisplay) || 0) / 100"
              height="448"
              :fill="appearance.isCharging ? '#22c55e' : 'var(--icon-bg)'"
              clip-path="url(#hw-bdyn-clip)"
            />
            <g fill="currentColor">
              <path :d="huaweiIcons.battery64.frame.d" :transform="huaweiIcons.battery64.frame.transform" />
              <path :d="huaweiIcons.battery64.tip.d" :transform="huaweiIcons.battery64.tip.transform" />
            </g>
            <text
              x="550"
              y="354"
              dominant-baseline="central"
              text-anchor="middle"
              font-family="'HarmonyOS Sans', 'DIN Alternate', sans-serif"
              font-weight="bold"
              :font-size="Number(batteryDisplay) >= 100 ? 340 : 385"
              fill="currentColor"
              letter-spacing="-5"
            >
              {{ batteryDisplay }}
            </text>
          </svg>
        </div>
      </template>

      <!-- 默认机型原有状态栏图标 (保持原样不动) -->
      <template v-else>
        <!-- 静音图标 (实心铃铛+斜杠) -->
        <div class="android-icon mute">
          <svg viewBox="0 0 32 32" width="100%" height="100%" aria-label="静音">
            <mask id="mute-mask">
              <rect width="32" height="32" fill="white" />
              <line x1="4" y1="4" x2="28" y2="28" stroke="black" stroke-width="5.5" stroke-linecap="round" />
            </mask>
            <g mask="url(#mute-mask)">
              <g transform="translate(16, 14) scale(1.15) translate(-16, -14)">
                <path d="M 16 3 C 11 3 8.5 7 8.5 12.5 V 17 L 5 22 H 27 L 23.5 17 V 12.5 C 23.5 7 21 3 16 3 Z" fill="currentColor" />
                <path d="M 12.5 23 C 12.5 24.5 14 26 16 26 C 18 26 19.5 24.5 19.5 23 Z" fill="currentColor" />
              </g>
            </g>
            <line x1="4" y1="4" x2="28" y2="28" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
          </svg>
        </div>

        <!-- 实时网速 -->
        <div class="android-icon network-speed">
          <span class="speed-number">{{ networkSpeed }}</span>
          <span class="speed-unit">KB/s</span>
        </div>

        <!-- 网络信号 -->
        <div class="android-icon mobile-signal">
          <span class="network-type">{{ appearance.networkType === 'default' ? randomNetworkType : appearance.networkType }}</span>
          <svg class="signal-svg" viewBox="0 0 34 20" width="100%">
            <rect
              v-for="bar in 4"
              :key="bar"
              :x="(bar - 1) * 9"
              :y="20 - (bar * 4 + 4)"
              width="5.5"
              :height="bar * 4 + 4"
              rx="2.5"
              :fill="bar <= (appearance.phoneSignal === 'default' ? randomPhone : Number(appearance.phoneSignal)) ? 'currentColor' : 'var(--icon-bg)'"
            />
          </svg>
        </div>

        <!-- Wi-Fi 信号 -->
        <div class="android-icon wifi">
          <svg viewBox="0 5.4 31.2 20.6" width="100%" height="100%">
            <path d="M 2.57 12.57 A 19 19 0 0 1 29.43 12.57" fill="none" :stroke="(appearance.wifiSignal === 'default' ? randomWifi : Number(appearance.wifiSignal)) >= 4 ? 'currentColor' : 'var(--icon-bg)'" stroke-width="3.2" stroke-linecap="butt" />
            <path d="M 6.1 16.1 A 14 14 0 0 1 25.9 16.1" fill="none" :stroke="(appearance.wifiSignal === 'default' ? randomWifi : Number(appearance.wifiSignal)) >= 3 ? 'currentColor' : 'var(--icon-bg)'" stroke-width="3.2" stroke-linecap="butt" />
            <path d="M 9.64 19.64 A 9 9 0 0 1 22.36 19.64" fill="none" :stroke="(appearance.wifiSignal === 'default' ? randomWifi : Number(appearance.wifiSignal)) >= 1 ? 'currentColor' : 'var(--icon-bg)'" stroke-width="3.2" stroke-linecap="butt" />
            <path d="M 12.5 22.5 A 5 5 0 0 1 19.5 22.5 L 16 26 Z" :fill="(appearance.wifiSignal === 'default' ? randomWifi : Number(appearance.wifiSignal)) >= 1 ? 'currentColor' : 'var(--icon-bg)'" />
            <polygon points="29,16 31,20 27,20" fill="currentColor" />
            <polygon points="29,26 31,22 27,22" fill="currentColor" />
          </svg>
        </div>

        <!-- 动态电池 -->
        <div class="android-icon battery">
          <svg viewBox="0 0 54 28" width="100%" height="100%">
            <defs>
              <clipPath id="battery-clip">
                <rect x="0" y="0" width="48" height="28" rx="5" />
              </clipPath>
            </defs>
            <rect x="0" y="0" width="48" height="28" rx="5" fill="var(--icon-bg)" />
            <rect
              x="0"
              y="0"
              :width="48 * appearance.phoneBattery / 100"
              height="28"
              :fill="appearance.isCharging ? '#22c55e' : 'currentColor'"
              clip-path="url(#battery-clip)"
            />
            <path d="M 48 9 H 49.5 Q 51.5 9 51.5 11 V 17 Q 51.5 19 49.5 19 H 48 Z" fill="var(--icon-bg)" />
            <text
              x="24"
              y="22"
              text-anchor="middle"
              font-size="20"
              font-weight="bold"
              font-family="Roboto, Arial, sans-serif"
              class="battery-text"
              :fill="appearance.darkMode ? '#000' : '#fff'"
            >
              {{ appearance.phoneBattery }}
            </text>
          </svg>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import useStore from "@/WechatTool/store";
import { huaweiIcons } from './huaweiIcons';
const { useSystemStore } = useStore();

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

const huaweiPhoneTimeHour = computed(() => {
  const h = props.appearance?.phoneTimeHour ?? useSystemStore.appearance?.phoneTimeHour ?? '';
  return String(h).replace(/^0(?=\d)/, '');
});

const batteryDisplay = computed(() => {
  return String(props.appearance?.phoneBattery ?? 100);
});

const dinDigits = {
  '0': { path: 'M5.8457 25.3157Q6.7414 27.8614 9.7586 27.8614Q12.7757 27.8614 13.7186 25.3157Q13.86 24.9386 13.9307 24.4671Q14.0014 23.9957 14.0486 23.0057Q14.0957 22.0157 14.1193 20.3657Q14.1429 18.7157 14.1429 16.0286Q14.1429 13.3414 14.1193 11.6914Q14.0957 10.0414 14.0486 9.0514Q14.0014 8.0614 13.9307 7.59Q13.86 7.1186 13.7186 6.7414Q12.7757 4.1957 9.7586 4.1957Q6.7414 4.1957 5.8457 6.7414Q5.7043 7.1186 5.6336 7.59Q5.5629 8.0614 5.5157 9.0514Q5.4686 10.0414 5.445 11.6914Q5.4214 13.3414 5.4214 16.0286Q5.4214 18.7157 5.445 20.3657Q5.4686 22.0157 5.5157 23.0057Q5.5629 23.9957 5.6336 24.4671Q5.7043 24.9386 5.8457 25.3157ZM0.66 26.3057Q0.5186 25.8343 0.3771 25.1979Q0.2357 24.5614 0.165 23.4536Q0.0943 22.3457 0.0471 20.5779Q0 18.81 0 16.0286Q0 13.2471 0.0471 11.4793Q0.0943 9.7114 0.165 8.6036Q0.2357 7.4957 0.3771 6.8829Q0.5186 6.27 0.66 5.7514Q1.6029 2.7343 3.8893 1.1079Q6.1757 -0.5186 9.7586 -0.5186Q13.3414 -0.5186 15.6279 1.1079Q17.9143 2.7343 18.9043 5.7514Q19.0457 6.27 19.1871 6.8829Q19.3286 7.4957 19.3993 8.6036Q19.47 9.7114 19.5171 11.4793Q19.5643 13.2471 19.5643 16.0286Q19.5643 18.81 19.5171 20.5779Q19.47 22.3457 19.3993 23.4536Q19.3286 24.5614 19.1871 25.1979Q19.0457 25.8343 18.9043 26.3057Q17.9143 29.3229 15.6279 30.9493Q13.3414 32.5757 9.7586 32.5757Q6.1757 32.5757 3.8893 30.9493Q1.6029 29.3229 0.66 26.3057Z', width: 19.56 },
  '1': { path: 'M5.5157 6.3171H5.4214L0.5186 9.7586Q0 10.0886 0 9.4757V4.6671Q0 4.29 0.33 4.0071L5.4686 0.2829Q5.7986 0 6.3171 0H10.3243Q10.7957 0 10.7957 0.4714V31.5857Q10.7957 32.0571 10.3243 32.0571H5.9871Q5.5157 32.0571 5.5157 31.5857Z', width: 10.8 },
  '2': { path: 'M0.0157 28.05Q0.0157 27.6729 0.2514 27.4371L11.5657 13.3414Q12.5086 12.1629 13.0743 10.9843Q13.64 9.8057 13.64 8.4386Q13.64 6.6471 12.5321 5.4214Q11.4243 4.1957 9.3971 4.1957Q7.4643 4.1957 6.38 5.28Q5.2957 6.3643 5.06 8.2029Q4.9657 8.6743 4.5414 8.58L0.3929 7.7314Q-0.0786 7.6371 0.0157 7.1657Q0.1571 5.7514 0.8171 4.3843Q1.4771 3.0171 2.6557 1.9093Q3.8343 0.8014 5.555 0.1414Q7.2757 -0.5186 9.5386 -0.5186Q11.8014 -0.5186 13.5457 0.1886Q15.29 0.8957 16.4921 2.0979Q17.6943 3.3 18.3307 4.9264Q18.9671 6.5529 18.9671 8.4386Q18.9671 10.6071 18.1657 12.4221Q17.3643 14.2371 15.95 15.9343L6.6157 27.2486V27.3429H18.4957Q18.9671 27.3429 18.9671 27.8143V31.5857Q18.9671 32.0571 18.4957 32.0571H0.4871Q0.0157 32.0571 0.0157 31.5857Z', width: 18.97 },
  '3': { path: 'M0.0157 25.6929Q-0.0786 25.2214 0.3929 25.08L4.4943 24.1371Q4.9186 24.0429 5.06 24.4671Q5.5786 25.8814 6.7571 26.8714Q7.9357 27.8614 9.9157 27.8614Q12.1786 27.8614 13.4043 26.5179Q14.63 25.1743 14.63 23.1Q14.63 20.6486 13.2157 19.2579Q11.8014 17.8671 9.3971 17.8671H8.03Q7.5586 17.8671 7.5586 17.3957V13.6714Q7.5586 13.2 8.03 13.2H9.3029Q11.4243 13.2 12.6971 11.9271Q13.97 10.6543 13.97 8.5329Q13.97 6.6 12.8386 5.3979Q11.7071 4.1957 9.68 4.1957Q7.8886 4.1957 6.8514 5.0914Q5.8143 5.9871 5.39 7.4957Q5.2486 7.92 4.8243 7.8257L0.8171 6.8829Q0.3457 6.7886 0.44 6.3171Q0.7229 4.8557 1.5007 3.6064Q2.2786 2.3571 3.4807 1.4379Q4.6829 0.5186 6.3093 0Q7.9357 -0.5186 9.8686 -0.5186Q12.1314 -0.5186 13.8757 0.1414Q15.62 0.8014 16.8221 1.98Q18.0243 3.1586 18.6607 4.785Q19.2971 6.4114 19.2971 8.3443Q19.2971 10.3714 18.4014 12.0921Q17.5057 13.8129 15.7143 14.9914V15.0857Q16.4214 15.3686 17.1757 16.0521Q17.93 16.7357 18.5429 17.7257Q19.1557 18.7157 19.5564 20.0121Q19.9571 21.3086 19.9571 22.8643Q19.9571 25.08 19.2029 26.8714Q18.4486 28.6629 17.105 29.9357Q15.7614 31.2086 13.9229 31.8921Q12.0843 32.5757 9.9157 32.5757Q6.1443 32.5757 3.4571 30.7843Q0.77 28.9929 0.0157 25.6929Z', width: 19.96 },
  '4': { path: 'M0.4714 27.1543Q0 27.1543 0 26.6829V23.0529Q0 22.7229 0.1414 22.4871L10.5129 0.3771Q10.7014 0 11.1729 0H15.6514Q16.17 0 15.9814 0.4243L5.7986 22.3457V22.44H13.0586Q13.3414 22.44 13.3414 22.1571V14.1429Q13.3414 13.6714 13.8129 13.6714H18.15Q18.6214 13.6714 18.6214 14.1429V22.1571Q18.6214 22.44 18.9043 22.44H21.2614Q21.7329 22.44 21.7329 22.9114V26.6829Q21.7329 27.1543 21.2614 27.1543H18.9043Q18.6214 27.1543 18.6214 27.4371V31.5857Q18.6214 32.0571 18.15 32.0571H13.8129Q13.3414 32.0571 13.3414 31.5857V27.4371Q13.3414 27.1543 13.0586 27.1543H0.4714Z', width: 21.73 },
  '5': { path: 'M0.0157 25.9757Q-0.0786 25.5514 0.3929 25.41L4.4 24.42Q4.8243 24.3729 4.9657 24.7971Q5.4371 26.1643 6.5214 27.0129Q7.6057 27.8614 9.3971 27.8614Q10.7643 27.8614 11.8486 27.1779Q12.9329 26.4943 13.3571 25.2214Q13.5929 24.5614 13.6871 23.7364Q13.7814 22.9114 13.7814 21.6857Q13.7814 20.3657 13.6871 19.5643Q13.5929 18.7629 13.3571 18.15Q12.8857 16.7357 11.8014 16.1229Q10.7171 15.51 9.35 15.51Q7.7471 15.51 6.7807 16.2171Q5.8143 16.9243 5.4371 17.7257Q5.2486 18.1971 4.8714 18.1971H0.9114Q0.44 18.1971 0.44 17.7257V0.4714Q0.44 0 0.9114 0H17.9771Q18.4486 0 18.4486 0.4714V4.2429Q18.4486 4.7143 17.9771 4.7143H5.5786Q5.2957 4.7143 5.2957 4.9971V12.21H5.4371Q6.0029 11.7386 7.205 11.2671Q8.4071 10.7957 10.1514 10.7957Q13.2629 10.7957 15.4079 12.1864Q17.5529 13.5771 18.4014 16.2171Q18.7314 17.2543 18.92 18.48Q19.1086 19.7057 19.1086 21.6857Q19.1086 24.75 18.4486 26.73Q17.5057 29.5586 15.0543 31.0671Q12.6029 32.5757 9.3971 32.5757Q7.5586 32.5757 5.9557 32.1043Q4.3529 31.6329 3.1271 30.7607Q1.9014 29.8886 1.1 28.6864Q0.2986 27.4843 0.0157 25.9757Z', width: 19.11 },
  '6': { path: 'M5.3743 22.77Q5.3743 25.0329 6.6707 26.4471Q7.9671 27.8614 10.23 27.8614Q12.4929 27.8614 13.8129 26.4471Q15.1329 25.0329 15.1329 22.77Q15.1329 20.5071 13.8129 19.0929Q12.4929 17.6786 10.23 17.6786Q7.9671 17.6786 6.6707 19.0929Q5.3743 20.5071 5.3743 22.77ZM0 22.6757Q0 20.7429 0.5893 18.8807Q1.1786 17.0186 2.1214 15.3214L10.5129 0.2829Q10.7014 0 11.0786 0H15.6043Q16.1229 0 15.8871 0.4714L8.8157 13.2943L8.91 13.3886Q9.2871 13.2 9.9236 13.0821Q10.56 12.9643 11.3143 12.9643Q13.1529 12.9643 14.8264 13.6243Q16.5 14.2843 17.7493 15.51Q18.9986 16.7357 19.7293 18.48Q20.46 20.2243 20.46 22.44Q20.46 24.8914 19.6586 26.7771Q18.8571 28.6629 17.49 29.9593Q16.1229 31.2557 14.2371 31.9157Q12.3514 32.5757 10.23 32.5757Q8.1086 32.5757 6.2229 31.9157Q4.3371 31.2557 2.97 29.9829Q1.6029 28.71 0.8014 26.8714Q0 25.0329 0 22.6757Z', width: 20.46 },
  '7': { path: 'M13.2471 4.8557V4.7143H5.28Q4.9971 4.7143 4.9971 4.9971V8.6743Q4.9971 9.1457 4.5257 9.1457H0.4714Q0 9.1457 0 8.6743V0.4714Q0 0 0.4714 0H18.4329Q18.9043 0 18.9043 0.4714V4.1486Q18.9043 4.6671 18.7629 4.9971L8.1557 31.6329Q8.0614 31.8686 7.9436 31.9629Q7.8257 32.0571 7.5429 32.0571H3.0643Q2.5457 32.0571 2.7814 31.5386Z', width: 18.9 },
  '8': { path: 'M5.3271 22.7229Q5.3271 24.9857 6.6943 26.4236Q8.0614 27.8614 10.3243 27.8614Q12.6343 27.8614 14.0014 26.4236Q15.3686 24.9857 15.3686 22.7229Q15.3686 20.46 14.0014 19.0221Q12.6343 17.5843 10.3243 17.5843Q8.0614 17.5843 6.6943 19.0221Q5.3271 20.46 5.3271 22.7229ZM10.3243 12.87Q12.3043 12.87 13.4829 11.5736Q14.6614 10.2771 14.6614 8.5329Q14.6614 6.7414 13.4829 5.4686Q12.3043 4.1957 10.3243 4.1957Q8.3443 4.1957 7.1893 5.4686Q6.0343 6.7414 6.0343 8.5329Q6.0343 10.2771 7.1893 11.5736Q8.3443 12.87 10.3243 12.87ZM0 22.9586Q0 20.2243 1.1786 18.2679Q2.3571 16.3114 4.0071 15.2743V15.18Q2.7814 14.3786 1.7443 12.6814Q0.7071 10.9843 0.7071 8.6271Q0.7071 6.8357 1.3436 5.1857Q1.98 3.5357 3.2057 2.2629Q4.4314 0.99 6.2229 0.2357Q8.0143 -0.5186 10.3243 -0.5186Q12.6343 -0.5186 14.4493 0.2357Q16.2643 0.99 17.49 2.2629Q18.7157 3.5357 19.3521 5.1857Q19.9886 6.8357 19.9886 8.6271Q19.9886 10.9843 18.9514 12.6814Q17.9143 14.3786 16.6886 15.18V15.2743Q18.3386 16.3114 19.5171 18.2679Q20.6957 20.2243 20.6957 22.9586Q20.6957 25.08 19.9414 26.8479Q19.1871 28.6157 17.7964 29.8886Q16.4057 31.1614 14.4964 31.8686Q12.5871 32.5757 10.3243 32.5757Q8.0614 32.5757 6.1757 31.8686Q4.29 31.1614 2.8993 29.8886Q1.5086 28.6157 0.7543 26.8479Q0 25.08 0 22.9586Z', width: 20.7 },
  '9': { path: 'M10.23 14.3786Q12.4929 14.3786 13.8129 12.9643Q15.1329 11.55 15.1329 9.2871Q15.1329 7.0243 13.8129 5.61Q12.4929 4.1957 10.23 4.1957Q7.9671 4.1957 6.6707 5.61Q5.3743 7.0243 5.3743 9.2871Q5.3743 11.55 6.6707 12.9643Q7.9671 14.3786 10.23 14.3786ZM11.6443 18.7629L11.55 18.6686Q11.22 18.8571 10.56 18.975Q9.9 19.0929 9.1457 19.0929Q7.3071 19.0929 5.6571 18.4329Q4.0071 17.7729 2.7343 16.5471Q1.4614 15.3214 0.7307 13.5771Q0 11.8329 0 9.6171Q0 7.1657 0.8014 5.28Q1.6029 3.3943 2.9936 2.0979Q4.3843 0.8014 6.2464 0.1414Q8.1086 -0.5186 10.23 -0.5186Q12.3986 -0.5186 14.2607 0.1414Q16.1229 0.8014 17.49 2.0743Q18.8571 3.3471 19.6586 5.1857Q20.46 7.0243 20.46 9.3814Q20.46 11.3143 19.8707 13.1764Q19.2814 15.0386 18.3386 16.7357L9.9943 31.7743Q9.8057 32.0571 9.4286 32.0571H4.8557Q4.3371 32.0571 4.5729 31.5857Z', width: 20.46 },
};

const batteryDigitsList = computed(() => {
  const str = batteryDisplay.value;
  let totalW = 0;
  const items = [];
  for (let i = 0; i < str.length; i++) {
    const ch = str[i];
    const data = dinDigits[ch] || dinDigits['0'];
    items.push({ ch, width: data.width, path: data.path, x: totalW });
    totalW += data.width + 4.5;
  }
  totalW -= 4.5;
  const startX = Math.round((102 - totalW) / 2);
  return items.map(item => ({
    ...item,
    x: startX + item.x,
  }));
});

const networkSpeed = ref('14.1');
const randomWifi = ref(4);
const randomPhone = ref(4);
const randomPhone1 = ref(5);
const randomPhone2 = ref(4);
const randomNetworkType = ref('5G');

let speedTimer = null;

const refreshRandoms = () => {
  networkSpeed.value = (0.1 + Math.random() * (512 - 0.1)).toFixed(1);

  const rWifi = Math.random();
  if (rWifi < 0.8) randomWifi.value = 4;
  else if (rWifi < 0.95) randomWifi.value = 3;
  else randomWifi.value = 2;

  const rPhone = Math.random();
  if (rPhone < 0.8) randomPhone.value = 4;
  else if (rPhone < 0.95) randomPhone.value = 3;
  else randomPhone.value = 2;

  // 华为机型 5格卡1信号 (独立随机): 75% 5格, 18% 4格, 5% 3格, 2% 2格
  const rPhone1 = Math.random();
  if (rPhone1 < 0.75) randomPhone1.value = 5;
  else if (rPhone1 < 0.93) randomPhone1.value = 4;
  else if (rPhone1 < 0.98) randomPhone1.value = 3;
  else randomPhone1.value = 2;

  // 华为机型 5格卡2信号 (独立随机): 70% 5格, 22% 4格, 6% 3格, 2% 2格
  const rPhone2 = Math.random();
  if (rPhone2 < 0.70) randomPhone2.value = 5;
  else if (rPhone2 < 0.92) randomPhone2.value = 4;
  else if (rPhone2 < 0.98) randomPhone2.value = 3;
  else randomPhone2.value = 2;

  const rNet = Math.random();
  if (rNet < 0.95) randomNetworkType.value = '5G';
  else randomNetworkType.value = '4G';
};

const currentWifiLevel = computed(() => {
  const sig = props.appearance?.wifiSignal ?? useSystemStore.appearance?.wifiSignal ?? 'default';
  if (sig === 'default') {
    return randomWifi.value;
  }
  return Number(sig) || 4;
});

const getWifiPathFill = (index) => {
  if (index === 0) return currentWifiLevel.value >= 4 ? 'currentColor' : 'var(--icon-bg)';
  if (index === 1) return currentWifiLevel.value >= 3 ? 'currentColor' : 'var(--icon-bg)';
  if (index === 2) return currentWifiLevel.value >= 2 ? 'currentColor' : 'var(--icon-bg)';
  if (index === 3) return currentWifiLevel.value >= 1 ? 'currentColor' : 'var(--icon-bg)';
  return currentWifiLevel.value >= 1 ? 'currentColor' : 'var(--icon-bg)';
};

const currentNetworkType = computed(() => {
  const net = props.appearance?.networkType ?? useSystemStore.appearance?.networkType ?? 'default';
  if (net === 'default') {
    return randomNetworkType.value;
  }
  return net;
});

const phoneSignalLevel1 = computed(() => {
  const sig = props.appearance?.phoneSignal ?? useSystemStore.appearance?.phoneSignal ?? 'default';
  if (sig === 'default') {
    return randomPhone1.value;
  }
  return Number(sig) || 5;
});

const phoneSignalLevel2 = computed(() => {
  const sig2 = props.appearance?.phoneSignal2 ?? useSystemStore.appearance?.phoneSignal2 ?? 'default';
  if (sig2 === 'default') {
    return randomPhone2.value;
  }
  return Number(sig2) || 5;
});

onMounted(() => {
  refreshRandoms();
  speedTimer = setInterval(() => {
    refreshRandoms();
  }, 5000);
});

onUnmounted(() => {
  if (speedTimer) clearInterval(speedTimer);
});
</script>

<style lang="less" scoped>
.phone-bar {
  height: var(--phone-bar-height, 132px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 45px 0 65px;
  position: relative;
  z-index: 99999;
  
  --icon-bg: rgba(0, 0, 0, 0.2);
  color: #000;
  
  &.dark {
    --icon-bg: rgba(255, 255, 255, 0.2);
    color: #fff;
  }

  .phone-time {
    position: absolute;
    left: 65px;
    top: var(--phone-bar-icon-top, 41px);
    height: 36px;
    line-height: 36px;
    font-size: 41px;
    font-family: "OPPO Sans", "HarmonyOS Sans", "Roboto", "Helvetica Neue", sans-serif;
    font-weight: 540;
    -webkit-text-stroke: 1px currentColor;
    letter-spacing: 1px;
    margin-top: 0px;
    display: flex;
    align-items: center;
  }

  .phone-status-icons {
    position: absolute;
    right: 45px;
    top: var(--phone-bar-icon-top, 41px);
    height: 36px;
    display: flex;
    align-items: flex-end;
    gap: 16px; 
    
    &.huawei-bar {
      right: 83px;
      width: auto;
      top: var(--phone-bar-icon-top, 51px);
      height: 43px;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 0;
      color: #494949;
      --icon-bg: #d0d0d0;

      .huawei-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: currentColor;

        &.alarm {
          width: 41.4px;
          height: 38.7px;
          margin-right: 17.7px;
        }
        &.mute {
          width: 34.4px;
          height: 38.7px;
          margin-right: 17.7px;
        }
        &.bluetooth {
          width: 23.1px;
          height: 39.8px;
          margin-right: 17.7px;
        }
        &.wifi {
          width: 50px;
          height: 38.7px;
          margin-right: 16px;
        }
        &.mobile-signal {
          width: 50.4px;
          height: 38.7px;
          .huawei-signal-svg {
            width: 100% !important;
            height: 100% !important;
            display: block;
          }
          &.first {
            margin-right: 18px;
          }
          &.second {
            margin-right: 21.1px;
          }
        }
        &.battery {
          width: 85.9px;
          height: 43px;
          margin-right: 0;
          .huawei-battery-svg {
            width: 100% !important;
            height: 100% !important;
            display: block;
          }
        }
      }
    }
  }

  &.dark {
    .phone-status-icons.huawei-bar,
    .huawei-time-box,
    .huawei-icon.eye {
      color: #fff;
      --icon-bg: rgba(255, 255, 255, 0.2);
    }
  }

  .huawei-time-box {
    position: absolute;
    left: 65px;
    top: var(--phone-bar-icon-top, 51px);
    display: flex;
    align-items: center;
    height: 43px;
    color: #494949;

    .phone-time {
      position: static;
      height: 43px;
      line-height: 43px;
      font-size: 43px; /* 华为系统时间文字大小增大2px至 35px */
      font-family: 'JunxiuRoundedNum', -apple-system-rounded, 'SF Pro Rounded', 'Arial Rounded MT Bold', 'HarmonyOS Sans Rounded', 'YouYuan', '幼圆', 'STYuanti-SC-Regular', '华文细圆', sans-serif;
      font-weight: 400; /* 粗细调细一点（原为600） */
      -webkit-text-stroke: 0.1px currentColor; /* 在此调整华为系统时间粗细标签（数值越大越粗，如 0px, 0.1px, 0.2px 等） */
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
    }
  }

  /* 眼睛图标：固定距离左侧 518px */
  .huawei-icon.eye {
    position: absolute;
    left: 518px;
    top: var(--phone-bar-icon-top, 51px);
    width: 56px;
    height: 43px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #494949;

    svg {
      width: 100%;
      height: 38px;
      display: block;
    }
  }

  .android-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }

  .mute {
    width: 36px;
    height: 36px;
  }

  .network-speed {
    display: flex;
    flex-direction: column;
    justify-content: flex-end; 
    align-items: flex-end;
    min-width: 45px;
    height: 36px;
    
    .speed-number {
      font-size: 22px;
      font-weight: 800;
      color: currentColor;
      line-height: 1;
      letter-spacing: -0.2px;
    }
    
    .speed-unit {
      font-size: 18px;
      font-weight: 700;
      color: currentColor;
      line-height: 1;
    }
  }

  .mobile-signal {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    position: relative;
    width: 52px;
    height: 36px;
    margin-right: -4px; /* Pulls wifi closer, shifting left icons right */
    
    .network-type {
      position: absolute;
      left: 4px;
      top: -2px; /* 向上偏移填满 3px 空隙 */
      font-size: 15px; 
      font-weight: 900;
      -webkit-text-stroke: 0.2px currentColor; 
      color: currentColor;
      line-height: 1;
    }
    
    .signal-svg {
      width: 43px; 
      height: 25px;
    }
  }

  .wifi {
    width: 55px; 
    height: 36px;
    margin: 0;
  }

  .battery {
    width: 69px; /* 36 * (54/28) ≈ 69.4 */
    height: 36px;
    
    .battery-text {
      /* font-size is now handled inside SVG for better scaling */
      letter-spacing: 0.5px;
    }
  }
}
</style>
