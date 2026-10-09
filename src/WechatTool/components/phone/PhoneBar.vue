<template>
  <div class="phone-bar" :class="{dark: appearance.darkMode}">
    <div class="phone-time">{{ appearance.phoneTimeHour }}:{{ appearance.phoneTimeMinute }}</div>
    <div class="phone-status-icons">
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
        
        <!-- 
          信号柱状图:
        -->
        <svg class="signal-svg" viewBox="0 0 34 20" width="100%">
          <!-- 
            循环 4 次生成 4 根信号条
          -->
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
          <!-- Level 4 -->
          <path d="M 2.57 12.57 A 19 19 0 0 1 29.43 12.57" fill="none" :stroke="(appearance.wifiSignal === 'default' ? randomWifi : Number(appearance.wifiSignal)) >= 4 ? 'currentColor' : 'var(--icon-bg)'" stroke-width="3.2" stroke-linecap="butt" />
          <!-- Level 3 -->
          <path d="M 6.1 16.1 A 14 14 0 0 1 25.9 16.1" fill="none" :stroke="(appearance.wifiSignal === 'default' ? randomWifi : Number(appearance.wifiSignal)) >= 3 ? 'currentColor' : 'var(--icon-bg)'" stroke-width="3.2" stroke-linecap="butt" />
          <!-- Level 2 -->
          <path d="M 9.64 19.64 A 9 9 0 0 1 22.36 19.64" fill="none" :stroke="(appearance.wifiSignal === 'default' ? randomWifi : Number(appearance.wifiSignal)) >= 2 ? 'currentColor' : 'var(--icon-bg)'" stroke-width="3.2" stroke-linecap="butt" />
          
          <!-- Level 1 (边缘完美对齐 45 度的底部圆润三角形) -->
          <path d="M 12.5 22.5 A 5 5 0 0 1 19.5 22.5 L 16 26 Z" :fill="(appearance.wifiSignal === 'default' ? randomWifi : Number(appearance.wifiSignal)) >= 1 ? 'currentColor' : 'var(--icon-bg)'" />
          
          <!-- 上下行箭头 (上移 2px, 右移 2px) -->
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
          <!-- 电池底色 -->
          <rect x="0" y="0" width="48" height="28" rx="5" fill="var(--icon-bg)" />
          <!-- 电量填充 -->
          <rect
            x="0"
            y="0"
            :width="48 * appearance.phoneBattery / 100"
            height="28"
            :fill="appearance.isCharging ? '#22c55e' : 'currentColor'"
            clip-path="url(#battery-clip)"
          />
          <!-- 电池正极 -->
          <path d="M 48 9 H 49.5 Q 51.5 9 51.5 11 V 17 Q 51.5 19 49.5 19 H 48 Z" fill="var(--icon-bg)" />
          <!-- 电池数字 -->
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  appearance: {
    type: Object,
    default: () => {},
  }
})

const networkSpeed = ref('14.1');
const randomWifi = ref(4);
const randomPhone = ref(4);
const randomNetworkType = ref('5G');

let speedTimer = null;

const refreshRandoms = () => {
  // 网速: 0.1kb - 512kb 之间随机
  networkSpeed.value = (0.1 + Math.random() * (512 - 0.1)).toFixed(1);

  // wifi信号概率: 80% 4格, 15% 3格, 5% 2格
  const rWifi = Math.random();
  if (rWifi < 0.8) randomWifi.value = 4;
  else if (rWifi < 0.95) randomWifi.value = 3;
  else randomWifi.value = 2;

  // 流量信号概率: 80% 4格, 15% 3格, 5% 2格
  const rPhone = Math.random();
  if (rPhone < 0.8) randomPhone.value = 4;
  else if (rPhone < 0.95) randomPhone.value = 3;
  else randomPhone.value = 2;

  // 手机信号文字: 95% 5G, 5% 4G
  const rNet = Math.random();
  if (rNet < 0.95) randomNetworkType.value = '5G';
  else randomNetworkType.value = '4G';
};

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
    top: 41px;
    height: 36px;
    line-height: 36px;
    font-size: 41px;
    font-family: "OPPO Sans", "HarmonyOS Sans", "Roboto", "Helvetica Neue", sans-serif;
    font-weight: 540; /* 落在较细的字重区间 */
    -webkit-text-stroke: 1px currentColor; /* 终极绝招：利用同色微量描边人工增粗！填补 540 和 550 之间的物理断层 */
    letter-spacing: 1px;
    margin-top: 0px;
    display: flex;
    align-items: center; /* Ensures text is perfectly centered within the 36px height */
  }

  .phone-status-icons {
    position: absolute;
    right: 45px;
    top: 41px;
    height: 36px;
    display: flex;
    align-items: flex-end; /* 对齐所有图标的底部 */
    gap: 16px; 
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
