<template>
  <div class="batch-studio">
    <!-- 左侧：具体的对话设置和外观设置的集成调整框 -->
    <div class="batch-col batch-left">
      <div class="panel-header">
        <div class="panel-title">
          <i class="title-icon">⚙️</i>
          <span>集成调整框</span>
          <span class="active-badge" v-if="currentTask">
            {{ currentTask.title }}
          </span>
        </div>
        <div class="panel-subtitle">调整当前选中图片的各项参数，右侧实时联动预览</div>
      </div>

      <div class="panel-body" v-if="currentTask">
        <a-tabs v-model:activeKey="activeTabKey" size="small" centered class="integrated-tabs">
          <!-- 标签 1：外观设置 -->
          <a-tab-pane key="appearance" tab="外观设置">
            <perfect-scrollbar class="tab-scroll-pane">
              <a-form layout="vertical" size="small" class="settings-form">
                <a-form-item label="手机机型">
                  <a-radio-group
                    v-model:value="currentTask.appearance.model"
                    button-style="solid"
                    size="small"
                    @change="handleAppearanceChange"
                  >
                    <a-radio-button value="huawei_junxiu">华为细圆</a-radio-button>
                    <a-radio-button value="android">默认机型</a-radio-button>
                  </a-radio-group>
                </a-form-item>

                <a-form-item label="对方用户名 / 聊天标题">
                  <a-input
                    v-model:value="currentTask.appearance.chatTitle"
                    placeholder="例如：派大星 或 对方"
                    @change="handleAppearanceChange"
                  />
                </a-form-item>

                <a-form-item label="手机时间">
                  <div class="time-select-row">
                    <a-select
                      v-model:value="currentTask.appearance.phoneTimeHour"
                      :options="hourOptions"
                      style="width: 72px"
                      @change="handleAppearanceChange"
                    />
                    <span class="time-colon">:</span>
                    <a-select
                      v-model:value="currentTask.appearance.phoneTimeMinute"
                      :options="minuteOptions"
                      style="width: 72px"
                      @change="handleAppearanceChange"
                    />
                    <a-button size="small" @click="setTimeToNow">设为当前</a-button>
                  </div>
                </a-form-item>

                <a-form-item label="手机电量">
                  <a-row :gutter="8" align="middle">
                    <a-col :span="16">
                      <a-slider
                        v-model:value="currentTask.appearance.phoneBattery"
                        :min="0"
                        :max="100"
                        :tip-formatter="(v) => `${v}%`"
                        @change="handleAppearanceChange"
                      />
                    </a-col>
                    <a-col :span="8">
                      <a-input-number
                        v-model:value="currentTask.appearance.phoneBattery"
                        :min="0"
                        :max="100"
                        style="width: 100%"
                        @change="handleAppearanceChange"
                      />
                    </a-col>
                  </a-row>
                </a-form-item>

                <div class="switches-grid">
                  <div class="switch-item">
                    <span>深色模式</span>
                    <a-switch
                      v-model:checked="currentTask.appearance.darkMode"
                      size="small"
                      @change="handleAppearanceChange"
                    />
                  </div>
                  <div class="switch-item">
                    <span>是否充电中</span>
                    <a-switch
                      v-model:checked="currentTask.appearance.isCharging"
                      size="small"
                      @change="handleAppearanceChange"
                    />
                  </div>
                  <div class="switch-item">
                    <span>听筒模式</span>
                    <a-switch
                      v-model:checked="currentTask.appearance.earphoneMode"
                      size="small"
                      @change="handleAppearanceChange"
                    />
                  </div>
                </div>

                <a-form-item label="未读消息数" style="margin-top: 10px;">
                  <a-input-number
                    v-model:value="currentTask.appearance.unreadMessages"
                    :min="0"
                    :max="999"
                    style="width: 120px"
                    @change="handleAppearanceChange"
                  />
                </a-form-item>

                <a-divider style="margin: 12px 0;">信号设置</a-divider>

                <a-form-item label="Wifi信号">
                  <a-select
                    v-model:value="currentTask.appearance.wifiSignal"
                    :options="wifiSignals"
                    @change="handleAppearanceChange"
                  />
                </a-form-item>

                <a-form-item :label="isHuaweiTask ? '流量信号 1' : '流量信号'">
                  <a-select
                    v-model:value="currentTask.appearance.phoneSignal"
                    :options="phoneSignals"
                    @change="handleAppearanceChange"
                  />
                </a-form-item>

                <a-form-item v-if="isHuaweiTask" label="流量信号 2">
                  <a-select
                    v-model:value="currentTask.appearance.phoneSignal2"
                    :options="phoneSignals"
                    @change="handleAppearanceChange"
                  />
                </a-form-item>

                <div class="sync-all-wrap">
                  <a-button type="dashed" block size="small" @click="syncAppearanceToAll">
                    将当前外观配置应用到全部图片
                  </a-button>
                </div>
              </a-form>
            </perfect-scrollbar>
          </a-tab-pane>

          <!-- 标签 2：对话设置 -->
          <a-tab-pane key="chat" tab="对话设置">
            <perfect-scrollbar class="tab-scroll-pane">
              <div class="chat-pane-inner">
                <!-- 当前图片的消息列表 -->
                <div class="message-list-header">
                  <span>当前图片消息 ({{ currentTask.chatList.length }}条)</span>
                  <a-button size="small" type="link" danger @click="clearCurrentTaskMessages">
                    清空消息
                  </a-button>
                </div>

                <div class="message-list-container">
                  <div
                    v-for="(msg, mIdx) in currentTask.chatList"
                    :key="msg.id || mIdx"
                    class="msg-item-card"
                    :class="{ 'is-own': msg.role === 'own' }"
                  >
                    <div class="msg-item-top">
                      <span class="msg-idx">#{{ mIdx + 1 }}</span>
                      <a-tag :color="msg.role === 'own' ? 'green' : 'blue'" class="role-tag">
                        {{ msg.role === 'own' ? '我' : '对方' }}
                      </a-tag>
                      <a-tag color="purple" class="type-tag">{{ getMsgTypeLabel(msg) }}</a-tag>
                      <div class="msg-item-actions">
                        <a-tooltip title="切换发送人 (我 ⇄ 对方)">
                          <a-button
                            size="small"
                            type="text"
                            @click="toggleMessageRole(mIdx)"
                          >⇄</a-button>
                        </a-tooltip>
                        <a-tooltip title="上移">
                          <a-button
                            size="small"
                            type="text"
                            :disabled="mIdx === 0"
                            @click="moveMessage(mIdx, -1)"
                          >↑</a-button>
                        </a-tooltip>
                        <a-tooltip title="下移">
                          <a-button
                            size="small"
                            type="text"
                            :disabled="mIdx === currentTask.chatList.length - 1"
                            @click="moveMessage(mIdx, 1)"
                          >↓</a-button>
                        </a-tooltip>
                        <a-popconfirm title="确认删除此条消息？" @confirm="deleteMessage(mIdx)">
                          <a-button size="small" type="text" danger>×</a-button>
                        </a-popconfirm>
                      </div>
                    </div>
                    <div class="msg-item-content">
                      <template v-if="msg.type === 'text'">
                        <a-textarea
                          v-model:value="msg.content"
                          :auto-size="{ minRows: 1, maxRows: 3 }"
                          size="small"
                          @change="handleChatModified"
                        />
                      </template>
                      <template v-else-if="msg.type === 'voice'">
                        <div class="inline-voice-edit">
                          <span>时长：</span>
                          <a-input-number
                            v-model:value="msg.duration"
                            :min="1"
                            :max="60"
                            size="small"
                            style="width: 70px"
                            @change="handleChatModified"
                          />
                          <span>秒</span>
                        </div>
                      </template>
                      <template v-else-if="msg.type === 'avInvite'">
                        <div class="inline-av-edit">
                          <span>通话时长：</span>
                          <a-input
                            v-model:value="msg.duration"
                            size="small"
                            style="width: 90px"
                            @change="handleChatModified"
                          />
                        </div>
                      </template>
                      <template v-else-if="msg.type === 'transferAccounts'">
                        <div class="inline-transfer-edit">
                          <span>金额 ¥</span>
                          <a-input-number
                            v-model:value="msg.money"
                            :min="0.01"
                            :precision="2"
                            size="small"
                            style="width: 90px"
                            @change="handleChatModified"
                          />
                          <a-input
                            v-model:value="msg.content"
                            placeholder="备注说明"
                            size="small"
                            style="flex: 1"
                            @change="handleChatModified"
                          />
                        </div>
                      </template>
                      <template v-else-if="msg.type === 'redEnvelope'">
                        <a-input
                          v-model:value="msg.content"
                          placeholder="红包祝福语"
                          size="small"
                          @change="handleChatModified"
                        />
                      </template>
                      <template v-else>
                        <a-input
                          v-model:value="msg.content"
                          size="small"
                          @change="handleChatModified"
                        />
                      </template>
                    </div>
                  </div>
                  <div v-if="!currentTask.chatList.length" class="empty-msgs">
                    当前图片暂无消息，请在下方添加
                  </div>
                </div>

                <!-- 添加新消息表单 -->
                <div class="add-msg-box">
                  <div class="add-msg-title">添加新消息</div>
                  <div class="add-msg-fields">
                    <div class="add-row">
                      <a-select
                        v-model:value="newMsgForm.type"
                        :options="msgTypeOptions"
                        size="small"
                        style="width: 110px"
                      />
                      <a-radio-group
                        v-model:value="newMsgForm.role"
                        button-style="solid"
                        size="small"
                        v-if="!['time', 'system'].includes(newMsgForm.type)"
                      >
                        <a-radio-button value="own">我</a-radio-button>
                        <a-radio-button value="other">对方</a-radio-button>
                      </a-radio-group>
                    </div>

                    <div class="add-row" v-if="newMsgForm.type === 'text'">
                      <a-textarea
                        v-model:value="newMsgForm.content"
                        placeholder="输入文本消息内容..."
                        :rows="2"
                        size="small"
                      />
                    </div>

                    <div class="add-row" v-else-if="newMsgForm.type === 'voice'">
                      <span>语音秒数：</span>
                      <a-input-number
                        v-model:value="newMsgForm.voiceSeconds"
                        :min="1"
                        :max="60"
                        size="small"
                        style="width: 80px"
                      />
                      <span>秒</span>
                    </div>

                    <div class="add-row" v-else-if="newMsgForm.type === 'avInvite'">
                      <span>通话时长：</span>
                      <a-input
                        v-model:value="newMsgForm.callDuration"
                        placeholder="00:10"
                        size="small"
                        style="width: 100px"
                      />
                    </div>

                    <div class="add-row" v-else-if="newMsgForm.type === 'transferAccounts'">
                      <span>金额：¥</span>
                      <a-input-number
                        v-model:value="newMsgForm.transferMoney"
                        :min="0.01"
                        :precision="2"
                        size="small"
                        style="width: 90px"
                      />
                      <a-input
                        v-model:value="newMsgForm.content"
                        placeholder="备注"
                        size="small"
                        style="flex: 1"
                      />
                    </div>

                    <div class="add-row" v-else-if="newMsgForm.type === 'redEnvelope'">
                      <a-input
                        v-model:value="newMsgForm.content"
                        placeholder="恭喜发财，大吉大利"
                        size="small"
                      />
                    </div>

                    <div class="add-row" v-else-if="newMsgForm.type === 'time'">
                      <a-input
                        v-model:value="newMsgForm.content"
                        placeholder="例如：昨天 上午11:20"
                        size="small"
                      />
                    </div>

                    <div class="add-row" v-else>
                      <a-input
                        v-model:value="newMsgForm.content"
                        placeholder="消息内容"
                        size="small"
                      />
                    </div>

                    <a-button type="primary" size="small" block @click="appendNewMessage">
                      + 添加到当前图片
                    </a-button>
                  </div>
                </div>
              </div>
            </perfect-scrollbar>
          </a-tab-pane>
        </a-tabs>
      </div>

      <div class="panel-empty" v-else>
        请在中间任务列表中选择或创建图片任务
      </div>
    </div>

    <!-- 中间：选择文件 / 批量文本输入与特殊符号划分 & 任务列表 -->
    <div class="batch-col batch-middle">
      <div class="panel-header">
        <div class="panel-title">
          <i class="title-icon">📝</i>
          <span>批量任务与文件</span>
        </div>
        <div class="panel-subtitle">复制文本或选择文件，使用 --- 划分多张图片</div>
      </div>

      <div class="middle-toolbar">
        <label class="file-picker-btn">
          <i class="btn-icon">📁</i> 选择文件导入
          <input type="file" accept=".txt,.json" hidden @change="handleFileSelected" />
        </label>
        <a-button size="small" @click="loadSampleBatchText">加载示例</a-button>
        <a-button size="small" @click="syncTasksToTextarea">从任务同步文本</a-button>
        <a-button size="small" danger @click="clearAllTasks">清空</a-button>
      </div>

      <!-- 批量文本输入框 -->
      <div class="batch-textarea-wrap">
        <div class="textarea-header">
          <span>批量文本输入框</span>
          <span class="delimiter-tag">划分符号：<code>---</code> 或 <code>===</code></span>
        </div>
        <a-textarea
          v-model:value="batchRawText"
          :rows="8"
          placeholder="在此直接粘贴多张图片的对话内容，不同图片之间用 --- 隔开，例如：&#10;机型：华为细圆&#10;手机时间：12:30&#10;对方用户名：派大星&#10;文本：我：你好派大星。&#10;文本：对方：你好GouTou！&#10;&#10;---&#10;&#10;手机时间：12:35&#10;文本：对方：好呀！"
          @blur="handleTextareaBlur"
        />
        <div class="textarea-actions">
          <a-button type="primary" size="small" @click="reparseBatchText">
            🔄 解析文本并更新任务列表
          </a-button>
        </div>
      </div>

      <!-- 任务列表 -->
      <div class="task-list-section">
        <div class="task-list-header">
          <span class="title">已划分图片任务 ({{ taskList.length }} 张)</span>
          <a-button size="small" type="primary" ghost @click="addNewTask">+ 新增一张图片</a-button>
        </div>

        <perfect-scrollbar class="task-cards-scroll">
          <div
            v-for="(task, index) in taskList"
            :key="task.id"
            class="task-card"
            :class="{ active: currentTaskIndex === index, 'is-done': task.status === 'done' }"
            @click="selectTask(index)"
          >
            <div class="task-card-main">
              <div class="task-card-header">
                <span class="task-card-title">{{ task.title }}</span>
                <span class="task-status-pill" :class="task.status">
                  {{ getTaskStatusText(task) }}
                </span>
              </div>
              <div class="task-card-meta">
                <a-tag size="small">{{ task.appearance.model === 'huawei_junxiu' ? '华为细圆' : '默认机型' }}</a-tag>
                <a-tag size="small">{{ task.appearance.phoneTimeHour }}:{{ task.appearance.phoneTimeMinute }}</a-tag>
                <a-tag size="small">{{ task.appearance.phoneBattery }}%电量</a-tag>
                <a-tag size="small" color="blue">{{ task.chatList.length }}条消息</a-tag>
              </div>
            </div>

            <div class="task-card-actions" @click.stop>
              <a-popconfirm title="确认删除此任务？" @confirm="deleteTask(index)">
                <a-button size="small" type="text" danger class="del-task-btn">×</a-button>
              </a-popconfirm>
            </div>
          </div>

          <div v-if="!taskList.length" class="empty-tasks">
            暂无任务，请在上方粘贴文本或选择文件导入
          </div>
        </perfect-scrollbar>
      </div>

      <!-- 中间底部快捷批量操作 -->
      <div class="middle-bottom-actions">
        <a-button
          type="primary"
          size="middle"
          block
          :loading="isGenerating"
          :disabled="!taskList.length"
          @click="handleBatchGenerate"
          class="gen-all-btn"
        >
          ⚡ 一键批量生成全部图片 ({{ taskList.length }} 张)
        </a-button>
        <a-button
          size="middle"
          block
          :disabled="!hasGeneratedImages"
          @click="handleBatchDownloadZip"
          class="download-zip-btn"
        >
          📦 批量打包下载全部 (ZIP)
        </a-button>
      </div>
    </div>

    <!-- 右侧：一个预览框与批量下载 -->
    <div class="batch-col batch-right">
      <div class="panel-header">
        <div class="panel-title">
          <i class="title-icon">📱</i>
          <span>生成预览框</span>
          <span class="preview-target" v-if="currentTask">
            - {{ currentTask.title }} ({{ currentTask.appearance.model === 'huawei_junxiu' ? '华为细圆' : '默认机型' }})
          </span>
        </div>
        <div class="panel-actions">
          <a-button
            size="small"
            type="primary"
            :loading="isGeneratingCurrent"
            @click="generateAndDownloadCurrent"
            :disabled="!currentTask"
          >
            下载当前图片
          </a-button>
          <a-button
            size="small"
            type="primary"
            ghost
            :loading="isGenerating"
            @click="handleBatchDownloadZip"
            :disabled="!taskList.length"
          >
            直接批量下载
          </a-button>
        </div>
      </div>

      <!-- 手机预览容器 -->
      <div class="preview-stage-container">
        <!-- 批量生成进度浮层 -->
        <div class="gen-progress-mask" v-if="isGenerating">
          <div class="progress-box">
            <a-spin size="large" />
            <div class="progress-text">
              正在批量生成：第 {{ currentGeneratingIndex + 1 }} / {{ taskList.length }} 张...
            </div>
            <a-progress :percent="generateProgress" stroke-color="#fd6e6a" />
          </div>
        </div>

        <perfect-scrollbar class="preview-stage-scroll">
          <div class="phone-wrap" :style="{ height: wrapperHeight + 'px' }" v-if="currentTask">
            <div class="phone-scale" :style="{ transform: `scale(${phoneScale})` }">
              <div
                id="phone"
                class="phone"
                :class="[useSystemStore.appearance.model, { 'dark': useSystemStore.appearance.darkMode }]"
                :style="phoneStyle"
              >
                <PhoneBar :appearance="useSystemStore.appearance" />
                <PhoneNav :appearance="useSystemStore.appearance" />
                <div class="phone-bg">
                  <img
                    :src="useSystemStore.appearance.chatBackground"
                    v-if="useSystemStore.appearance.chatBackground"
                    class="phone-bg-for-height"
                  />
                </div>
                <PhoneBody :appearance="useSystemStore.appearance" :emojiBase64="emojiBase64" />
                <PhoneBottom :appearance="useSystemStore.appearance" :emojiBase64="emojiBase64" />
              </div>
            </div>
          </div>
          <div class="empty-preview" v-else>
            暂无预览内容，请在中间选择图片任务
          </div>
        </perfect-scrollbar>
      </div>

      <!-- 底部已生成缩略图栏 -->
      <div class="generated-gallery-bar" v-if="hasGeneratedImages">
        <div class="gallery-title">
          <span>已生成截图 ({{ generatedCount }}/{{ taskList.length }})</span>
          <span class="gallery-tip">点击缩略图可单独下载</span>
        </div>
        <div class="gallery-items">
          <div
            v-for="(task, idx) in taskList"
            :key="task.id"
            class="thumb-item"
            v-show="task.generatedImage"
            @click="downloadSingleThumb(task, idx)"
          >
            <img :src="task.generatedImage" class="thumb-img" />
            <span class="thumb-label">{{ task.title }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted } from "vue";
import JSZip from "jszip";
import FileSaver from "file-saver";
import dayjs from "dayjs";
import { models, getModelConfig, wifiSignals, phoneSignals } from "@/WechatTool/utils/enum";
import {
  splitBatchText,
  parseBatchTasks,
  taskToText,
  batchTasksToText,
} from "@/WechatTool/utils/chatTextAdapter";
import { useHtmlToImage } from "@/WechatTool/hooks/useHtmlToImage";
import useStore from "@/WechatTool/store";
import { toast } from "@/WechatTool/utils/feedback";
import emojiBase64 from "@/WechatTool/utils/emojiBase64";

// 引入手机部件组件
import PhoneBar from "../phone/PhoneBar.vue";
import PhoneNav from "../phone/PhoneNav.vue";
import PhoneBody from "../phone/PhoneBody.vue";
import PhoneBottom from "../phone/PhoneBottom.vue";

const { useSystemStore, useUserStore, useChatStore } = useStore();
const { captureHtmlToImage } = useHtmlToImage();

// 状态定义
const activeTabKey = ref("appearance");
const currentTaskIndex = ref(0);
const taskList = ref([]);
const batchRawText = ref("");

const isGenerating = ref(false);
const isGeneratingCurrent = ref(false);
const currentGeneratingIndex = ref(0);
const generateProgress = ref(0);

// 手机预览几何尺寸计算
const phoneWidth = ref(1256);
const phoneHeight = ref(2760);
const phoneScale = ref(0.28);
const wrapperHeight = ref(772);
const phoneStyle = ref({});

const hourOptions = Array.from({ length: 24 }, (_, i) => ({
  value: String(i).padStart(2, "0"),
  label: String(i).padStart(2, "0"),
}));

const minuteOptions = Array.from({ length: 60 }, (_, i) => ({
  value: String(i).padStart(2, "0"),
  label: String(i).padStart(2, "0"),
}));

const msgTypeOptions = [
  { label: "文本消息", value: "text" },
  { label: "语音消息", value: "voice" },
  { label: "通话邀请", value: "avInvite" },
  { label: "转账", value: "transferAccounts" },
  { label: "红包", value: "redEnvelope" },
  { label: "时间戳", value: "time" },
  { label: "系统消息", value: "system" },
  { label: "拍一拍", value: "takeAPat" },
  { label: "撤回", value: "revoke" },
];

const newMsgForm = reactive({
  type: "text",
  role: "own",
  content: "",
  voiceSeconds: 5,
  callDuration: "00:10",
  transferMoney: 88,
});

const currentTask = computed(() => {
  if (currentTaskIndex.value >= 0 && currentTaskIndex.value < taskList.value.length) {
    return taskList.value[currentTaskIndex.value];
  }
  return null;
});

const isHuaweiTask = computed(() => {
  return currentTask.value?.appearance?.model === "huawei_junxiu";
});

const hasGeneratedImages = computed(() => {
  return taskList.value.some((t) => !!t.generatedImage);
});

const generatedCount = computed(() => {
  return taskList.value.filter((t) => !!t.generatedImage).length;
});

// 应用机型尺寸与CSS变量
const applyModelConfig = (modelVal) => {
  const currentModel = getModelConfig(modelVal || "huawei_junxiu");
  const { width, height } = currentModel;
  useSystemStore.phoneWidth = phoneWidth.value = width;
  useSystemStore.phoneHeight = phoneHeight.value = height;
  phoneScale.value = 340 / width;
  wrapperHeight.value = height * phoneScale.value;
  phoneStyle.value = {
    width: `${width}px`,
    height: `${height}px`,
    "--phone-bar-height": `${currentModel.barHeight}px`,
    "--phone-nav-height": `${currentModel.navHeight}px`,
    "--phone-content-top": `${currentModel.contentTop}px`,
    "--phone-content-bottom": `${currentModel.contentBottom}px`,
    "--phone-bottom-height": `${currentModel.bottomHeight}px`,
    "--phone-bottom-bar-display": currentModel.bottomBarDisplay || "none",
    "--phone-message-size": `${currentModel.messageSize}px`,
    "--phone-message-min-height": `${currentModel.messageMinHeight}px`,
    "--phone-message-padding-y": `${currentModel.messagePaddingY}px`,
    "--phone-message-padding-x": `${currentModel.messagePaddingX}px`,
    "--phone-message-line-height": `${currentModel.messageLineHeight}px`,
    "--phone-message-tail-top": `${currentModel.messageTailTop}px`,
    "--phone-avatar-size": `${currentModel.avatarSize}px`,
    "--phone-bar-icon-top": `${currentModel.barIconTop}px`,
    "--phone-bubble-margin-near": `${currentModel.bubbleMarginNear}px`,
    "--phone-bubble-margin-far": `${currentModel.bubbleMarginFar}px`,
    "--phone-username-size": `${currentModel.usernameSize}px`,
    "--phone-username-margin-left": `${currentModel.usernameMarginLeft}px`,
    "--phone-revoke-size": `${currentModel.revokeSize}px`,
    "--phone-revoke-weight": currentModel.revokeWeight || "500",
    "--phone-time-size": `${currentModel.timeSize}px`,
    "--phone-time-weight": currentModel.timeWeight || "normal",
    "--phone-item-padding-y": `${currentModel.itemPaddingY}px`,
    "--phone-time-padding-top": `${currentModel.timePaddingTop}px`,
    "--phone-time-padding-bottom": `${currentModel.timePaddingBottom}px`,
    "--phone-nav-title-size": `${currentModel.navTitleSize}px`,
    "--phone-nav-title-weight": currentModel.navTitleWeight || "500",
    "--phone-time-after-revoke-reduce": `${currentModel.timeAfterRevokeReduce || 0}px`,
    "--phone-time-before-revoke-reduce": `${currentModel.timeBeforeRevokeReduce || 0}px`,
    "--phone-revoke-after-time-reduce": `${currentModel.revokeAfterTimeReduce || 0}px`,
    "--phone-time-letter-spacing": `${currentModel.timeLetterSpacing || 0}px`,
    "--phone-revoke-letter-spacing": `${currentModel.revokeLetterSpacing || 0}px`,
    "--phone-av-icon-width": `${currentModel.avIconWidth || 50}px`,
    "--phone-av-icon-height": `${currentModel.avIconHeight || 21}px`,
    "--phone-av-icon-top": `${currentModel.avIconTop ?? 2}px`,
    "--phone-nav-earphone-width": `${currentModel.navEarphoneWidth || 36}px`,
    "--phone-nav-earphone-height": `${currentModel.navEarphoneHeight || 44}px`,
    "--phone-nav-earphone-margin-top": `${currentModel.navEarphoneMarginTop ?? 8}px`,
  };
};

// 同步任务到 Pinia store，使手机组件完整联动
const syncTaskToStore = (task) => {
  if (!task) return;
  // 外观同步
  Object.assign(useSystemStore.appearance, task.appearance);
  applyModelConfig(task.appearance.model);
  // 对话列表同步
  useChatStore.chatList = task.chatList || [];
  // 对方用户名同步
  if (task.appearance.chatTitle) {
    const otherUser =
      useUserStore.userList.find((u) => u.role === "other") ||
      (useUserStore.userList.length > 1 ? useUserStore.userList[1] : null);
    if (otherUser) {
      otherUser.nickname = task.appearance.chatTitle;
    }
  }
};

// 选定当前图片任务
const selectTask = (index) => {
  if (index >= 0 && index < taskList.value.length) {
    currentTaskIndex.value = index;
    syncTaskToStore(taskList.value[index]);
  }
};

// 外观设置发生改变
const handleAppearanceChange = () => {
  if (!currentTask.value) return;
  syncTaskToStore(currentTask.value);
};

// 对话内容修改
const handleChatModified = () => {
  if (!currentTask.value) return;
  useChatStore.chatList = [...currentTask.value.chatList];
};

// 快捷设为当前系统时间
const setTimeToNow = () => {
  if (!currentTask.value) return;
  const now = dayjs();
  currentTask.value.appearance.phoneTimeHour = now.format("HH");
  currentTask.value.appearance.phoneTimeMinute = now.format("mm");
  handleAppearanceChange();
};

// 将外观应用到全部图片
const syncAppearanceToAll = () => {
  if (!currentTask.value) return;
  const sourceApp = { ...currentTask.value.appearance };
  taskList.value.forEach((task) => {
    task.appearance = { ...sourceApp };
  });
  toast({ type: "success", content: "已将当前外观设置应用到全部图片任务" });
};

// 消息列表操作
const toggleMessageRole = (mIdx) => {
  if (!currentTask.value) return;
  const msg = currentTask.value.chatList[mIdx];
  msg.role = msg.role === "own" ? "other" : "own";
  const user =
    msg.role === "own"
      ? useUserStore.userList[0]
      : useUserStore.userList.find((u) => u.role === "other") || useUserStore.userList[1];
  msg.user = user;
  handleChatModified();
};

const moveMessage = (mIdx, offset) => {
  if (!currentTask.value) return;
  const list = currentTask.value.chatList;
  const target = mIdx + offset;
  if (target < 0 || target >= list.length) return;
  const temp = list[mIdx];
  list[mIdx] = list[target];
  list[target] = temp;
  handleChatModified();
};

const deleteMessage = (mIdx) => {
  if (!currentTask.value) return;
  currentTask.value.chatList.splice(mIdx, 1);
  handleChatModified();
};

const clearCurrentTaskMessages = () => {
  if (!currentTask.value) return;
  currentTask.value.chatList = [];
  handleChatModified();
};

const getMsgTypeLabel = (msg) => {
  const map = {
    text: "文本",
    voice: "语音",
    avInvite: "通话",
    transferAccounts: "转账",
    redEnvelope: "红包",
    time: "时间",
    system: "系统",
    takeAPat: "拍一拍",
    revoke: "撤回",
  };
  return map[msg.type] || msg.type;
};

// 添加新消息
const appendNewMessage = () => {
  if (!currentTask.value) return;
  const isOwn = newMsgForm.role === "own";
  const user = isOwn
    ? useUserStore.userList[0]
    : useUserStore.userList.find((u) => u.role === "other") || useUserStore.userList[1];
  const newId = `chat-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  let newChat = {
    id: newId,
    type: newMsgForm.type,
    role: newMsgForm.role,
    user,
    content: newMsgForm.content,
  };

  if (newMsgForm.type === "voice") {
    newChat.duration = Number(newMsgForm.voiceSeconds) || 5;
  } else if (newMsgForm.type === "avInvite") {
    newChat.invateType = "voice";
    newChat.state = "talked";
    newChat.duration = newMsgForm.callDuration || "00:10";
  } else if (newMsgForm.type === "transferAccounts") {
    newChat.money = Number(newMsgForm.transferMoney) || 88;
    newChat.received = false;
  } else if (newMsgForm.type === "redEnvelope") {
    newChat.money = 88;
    newChat.content = newMsgForm.content || "恭喜发财，大吉大利";
    newChat.received = false;
  }

  currentTask.value.chatList.push(newChat);
  handleChatModified();
  newMsgForm.content = "";
  toast({ type: "success", content: "已添加新消息" });
};

// 任务增删
const addNewTask = () => {
  const baseApp = currentTask.value
    ? { ...currentTask.value.appearance }
    : { ...useSystemStore.appearance };
  const newTask = {
    id: `task-${Date.now()}-${taskList.value.length}`,
    title: `图 ${taskList.value.length + 1}`,
    rawText: "",
    appearance: baseApp,
    chatList: [
      {
        id: `chat-${Date.now()}-1`,
        type: "text",
        role: "own",
        user: useUserStore.userList[0],
        content: "你好呀",
      },
    ],
    status: "idle",
    generatedImage: "",
  };
  taskList.value.push(newTask);
  selectTask(taskList.value.length - 1);
  toast({ type: "success", content: `已新建 ${newTask.title}` });
};

const deleteTask = (index) => {
  taskList.value.splice(index, 1);
  taskList.value.forEach((t, i) => {
    t.title = `图 ${i + 1}`;
  });
  if (currentTaskIndex.value >= taskList.value.length) {
    currentTaskIndex.value = Math.max(0, taskList.value.length - 1);
  }
  if (taskList.value.length > 0) {
    selectTask(currentTaskIndex.value);
  } else {
    useChatStore.chatList = [];
  }
};

const clearAllTasks = () => {
  taskList.value = [];
  batchRawText.value = "";
  currentTaskIndex.value = 0;
  useChatStore.chatList = [];
  toast({ type: "info", content: "已清空全部任务" });
};

const getTaskStatusText = (task) => {
  if (task.status === "generating") return "生成中...";
  if (task.status === "done" && task.generatedImage) return "已生成";
  return "待生成";
};

// 文本与任务互转
const reparseBatchText = () => {
  if (!batchRawText.value.trim()) {
    toast({ type: "warning", content: "请先粘贴或输入批量文本" });
    return;
  }
  const parsed = parseBatchTasks(batchRawText.value, useSystemStore.appearance, {
    userStore: useUserStore,
  });
  if (parsed.length) {
    taskList.value = parsed;
    currentTaskIndex.value = 0;
    selectTask(0);
    toast({ type: "success", content: `解析成功！已识别到 ${parsed.length} 张图片任务` });
  } else {
    toast({ type: "warning", content: "未能识别到有效对话，请检查格式后重试" });
  }
};

const handleTextareaBlur = () => {
  if (batchRawText.value.trim() && !taskList.value.length) {
    reparseBatchText();
  }
};

const syncTasksToTextarea = () => {
  if (!taskList.value.length) return;
  batchRawText.value = batchTasksToText(taskList.value, { userStore: useUserStore });
  toast({ type: "success", content: "已将任务列表逆向生成为批量文本" });
};

// 读取文件
const handleFileSelected = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.readAsText(file);
  reader.onload = (res) => {
    try {
      const content = res.target.result || "";
      batchRawText.value = content;
      reparseBatchText();
    } catch (err) {
      toast({ type: "error", content: "文件解析失败" });
    } finally {
      e.target.value = "";
    }
  };
};

// 加载示例数据
const loadSampleBatchText = () => {
  batchRawText.value = `机型：华为细圆
手机时间：12:30
手机电量：80%
对方用户名：派大星

文本：我：你好派大星。
文本：对方：你好GouTou！
语音：对方：5秒
通话：我：通话时长 00:10

---

机型：默认机型
手机时间：12:35
手机电量：79%
对方用户名：派大星

文本：我：周末有空一起喝奶茶吗？
文本：对方：好呀，什么时候？
转账：我：88.00元：奶茶基金

---

机型：华为细圆
手机时间：12:40
手机电量：78%
对方用户名：派大星

红包：对方：恭喜发财，大吉大利
文本：我：谢谢你的红包！
文本：对方：哈哈不客气~`;

  reparseBatchText();
};

// 生成单张图片
const generateAndDownloadCurrent = async () => {
  if (!currentTask.value) return;
  isGeneratingCurrent.value = true;
  try {
    syncTaskToStore(currentTask.value);
    await nextTick();
    await new Promise((r) => setTimeout(r, 150));
    const phoneEl = document.querySelector("#phone");
    if (!phoneEl) throw new Error("Phone element not found");
    const dataUrl = await captureHtmlToImage(phoneEl, {
      width: useSystemStore.phoneWidth,
      height: useSystemStore.phoneHeight,
    });
    currentTask.value.generatedImage = dataUrl;
    currentTask.value.status = "done";

    // 下载单张
    const byteString = atob(dataUrl.split(",")[1]);
    const mimeString = dataUrl.split(",")[0].split(":")[1].split(";")[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: mimeString });
    const filename = `${currentTask.value.title}_${currentTask.value.appearance.phoneTimeHour || "12"}${currentTask.value.appearance.phoneTimeMinute || "00"}.png`;
    FileSaver.saveAs(blob, filename);
    toast({ type: "success", content: `已生成并下载 ${currentTask.value.title}` });
  } catch (err) {
    toast({ type: "error", content: "生成图片失败：" + err.message });
  } finally {
    isGeneratingCurrent.value = false;
  }
};

// 批量生成全部图片
const handleBatchGenerate = async () => {
  if (!taskList.value.length) {
    toast({ type: "warning", content: "请先添加图片任务" });
    return;
  }

  isGenerating.value = true;
  generateProgress.value = 0;

  try {
    for (let i = 0; i < taskList.value.length; i++) {
      currentGeneratingIndex.value = i;
      currentTaskIndex.value = i;
      const task = taskList.value[i];
      task.status = "generating";
      syncTaskToStore(task);

      await nextTick();
      await new Promise((r) => setTimeout(r, 200));

      const phoneEl = document.querySelector("#phone");
      if (phoneEl) {
        const dataUrl = await captureHtmlToImage(phoneEl, {
          width: useSystemStore.phoneWidth,
          height: useSystemStore.phoneHeight,
        });
        task.generatedImage = dataUrl;
        task.status = "done";
      }

      generateProgress.value = Math.round(((i + 1) / taskList.value.length) * 100);
    }

    toast({
      type: "success",
      content: `全部 ${taskList.value.length} 张图片生成完成！可直接点击【批量下载】`,
    });
  } catch (err) {
    toast({ type: "error", content: "批量生成中出错：" + err.message });
  } finally {
    isGenerating.value = false;
  }
};

// 批量打包下载 ZIP
const handleBatchDownloadZip = async () => {
  if (!taskList.value.length) {
    toast({ type: "warning", content: "当前没有任务" });
    return;
  }

  // 若有未生成的图片，先自动进行批量生成
  const ungenerated = taskList.value.filter((t) => !t.generatedImage);
  if (ungenerated.length > 0) {
    toast({ type: "info", content: "正在自动生成未完成的图片，请稍候..." });
    await handleBatchGenerate();
  }

  try {
    const zip = new JSZip();
    taskList.value.forEach((task, idx) => {
      if (task.generatedImage) {
        const base64Data = task.generatedImage.replace(/^data:image\/png;base64,/, "");
        const hour = task.appearance.phoneTimeHour || "12";
        const min = task.appearance.phoneTimeMinute || "00";
        const title = task.title.replace(/[\\/:*?"<>|]/g, "_");
        const filename = `${idx + 1}_${title}_${hour}${min}.png`;
        zip.file(filename, base64Data, { base64: true });
      }
    });

    const zipBlob = await zip.generateAsync({ type: "blob" });
    const zipName = `批量聊天截图_${dayjs().format("YYYYMMDDHHmmss")}.zip`;
    FileSaver.saveAs(zipBlob, zipName);
    toast({ type: "success", content: `批量截图压缩包已下载：${zipName}` });
  } catch (err) {
    toast({ type: "error", content: "打包下载失败：" + err.message });
  }
};

// 点击缩略图单独下载
const downloadSingleThumb = (task, idx) => {
  if (!task.generatedImage) return;
  const byteString = atob(task.generatedImage.split(",")[1]);
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  const blob = new Blob([ab], { type: "image/png" });
  FileSaver.saveAs(blob, `${idx + 1}_${task.title}.png`);
  toast({ type: "success", content: `已下载 ${task.title}` });
};

// 初始化
onMounted(() => {
  loadSampleBatchText();
});
</script>

<style lang="less" scoped>
.batch-studio {
  display: flex;
  width: 100%;
  height: calc(100vh - 50px);
  background-color: var(--border-color);
  overflow: hidden;

  .batch-col {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--bg-color);

    .panel-header {
      padding: 12px 16px;
      border-bottom: 1px solid var(--border-color);
      background: var(--bg-color);

      .panel-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 15px;
        font-weight: 600;
        color: var(--text-color);

        .title-icon {
          font-style: normal;
          font-size: 16px;
        }

        .active-badge {
          font-size: 12px;
          background: #fd6e6a;
          color: #fff;
          padding: 1px 8px;
          border-radius: 10px;
          font-weight: normal;
        }
      }

      .panel-subtitle {
        font-size: 12px;
        color: #888;
        margin-top: 4px;
      }
    }
  }

  // 左侧集成调整框
  .batch-left {
    width: 370px;
    border-right: 1px solid var(--border-color);
    flex-shrink: 0;

    .integrated-tabs {
      height: 100%;
      :deep(.ant-tabs-content) {
        height: calc(100% - 46px);
      }
      :deep(.ant-tabs-tabpane) {
        height: 100%;
      }
    }

    .tab-scroll-pane {
      height: calc(100vh - 165px);
      padding: 14px 16px;
    }

    .settings-form {
      .time-select-row {
        display: flex;
        align-items: center;
        gap: 6px;
        .time-colon {
          font-weight: bold;
        }
      }

      .switches-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 10px;
        background: rgba(0, 0, 0, 0.02);
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 12px;

        .switch-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 13px;
        }
      }

      .sync-all-wrap {
        margin-top: 16px;
      }
    }

    .chat-pane-inner {
      .message-list-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 10px;
      }

      .message-list-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 16px;

        .msg-item-card {
          border: 1px solid var(--border-color);
          border-radius: 6px;
          padding: 8px;
          background: rgba(0, 0, 0, 0.01);
          transition: all 0.2s;

          &.is-own {
            border-left: 3px solid #52c41a;
          }
          &:not(.is-own) {
            border-left: 3px solid #1890ff;
          }

          .msg-item-top {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 6px;

            .msg-idx {
              font-size: 11px;
              color: #999;
            }
            .role-tag,
            .type-tag {
              margin: 0;
              font-size: 11px;
              padding: 0 4px;
              line-height: 18px;
            }
            .msg-item-actions {
              margin-left: auto;
              display: flex;
              gap: 2px;
            }
          }

          .inline-voice-edit,
          .inline-av-edit,
          .inline-transfer-edit {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
          }
        }

        .empty-msgs {
          text-align: center;
          color: #999;
          font-size: 12px;
          padding: 20px 0;
        }
      }

      .add-msg-box {
        border-top: 1px dashed var(--border-color);
        padding-top: 12px;

        .add-msg-title {
          font-size: 13px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .add-msg-fields {
          display: flex;
          flex-direction: column;
          gap: 8px;

          .add-row {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
          }
        }
      }
    }

    .panel-empty {
      padding: 40px 20px;
      text-align: center;
      color: #999;
    }
  }

  // 中间任务与文件
  .batch-middle {
    width: 420px;
    border-right: 1px solid var(--border-color);
    flex-shrink: 0;
    padding: 0;

    .middle-toolbar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      background: rgba(0, 0, 0, 0.02);
      border-bottom: 1px solid var(--border-color);

      .file-picker-btn {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        background: #1890ff;
        color: #fff;
        font-size: 12px;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.2s;

        &:hover {
          background: #40a9ff;
        }
      }
    }

    .batch-textarea-wrap {
      padding: 12px 14px;
      border-bottom: 1px solid var(--border-color);

      .textarea-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        font-size: 12px;
        font-weight: 600;

        .delimiter-tag {
          font-size: 11px;
          font-weight: normal;
          color: #888;
          code {
            color: #fd6e6a;
            font-weight: bold;
          }
        }
      }

      .textarea-actions {
        margin-top: 8px;
        display: flex;
        justify-content: flex-end;
      }
    }

    .task-list-section {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .task-list-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 600;
        border-bottom: 1px solid var(--border-color);
      }

      .task-cards-scroll {
        flex: 1;
        padding: 10px 14px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 8px;

        .task-card {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 10px 12px;
          border-radius: 8px;
          border: 1px solid var(--border-color);
          background: #fff;
          cursor: pointer;
          transition: all 0.2s;

          &:hover {
            border-color: #fd6e6a;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
          }

          &.active {
            border-color: #fd6e6a;
            background: rgba(253, 110, 106, 0.06);
            font-weight: 500;
          }

          &.is-done {
            border-left: 3px solid #52c41a;
          }

          .task-card-main {
            flex: 1;

            .task-card-header {
              display: flex;
              align-items: center;
              gap: 8px;
              margin-bottom: 6px;

              .task-card-title {
                font-size: 14px;
                font-weight: 600;
                color: var(--text-color);
              }

              .task-status-pill {
                font-size: 11px;
                padding: 1px 6px;
                border-radius: 10px;
                background: #f0f0f0;
                color: #666;

                &.done {
                  background: #f6ffed;
                  color: #52c41a;
                  border: 1px solid #b7eb8f;
                }
                &.generating {
                  background: #e6f7ff;
                  color: #1890ff;
                }
              }
            }

            .task-card-meta {
              display: flex;
              flex-wrap: wrap;
              gap: 4px;
              :deep(.ant-tag) {
                margin: 0;
                font-size: 11px;
                line-height: 18px;
              }
            }
          }

          .task-card-actions {
            margin-left: 8px;
            .del-task-btn {
              font-size: 16px;
              color: #999;
              &:hover {
                color: #ff4d4f;
              }
            }
          }
        }

        .empty-tasks {
          text-align: center;
          color: #999;
          font-size: 12px;
          padding: 30px 0;
        }
      }
    }

    .middle-bottom-actions {
      padding: 12px 14px;
      border-top: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 8px;
      background: var(--bg-color);

      .gen-all-btn {
        background-image: linear-gradient(135deg, #fd6e6a 10%, #ffc600 100%);
        border: none;
        font-weight: bold;
        color: #fff;
        height: 38px;
        border-radius: 6px;
        transition: all 0.3s;

        &:hover {
          opacity: 0.9;
          box-shadow: 0 4px 12px rgba(253, 110, 106, 0.4);
        }
      }

      .download-zip-btn {
        height: 36px;
        font-weight: 500;
        border-radius: 6px;
      }
    }
  }

  // 右侧生成预览框
  .batch-right {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .preview-target {
        font-size: 13px;
        font-weight: normal;
        color: #666;
      }
      .panel-actions {
        display: flex;
        gap: 8px;
      }
    }

    .preview-stage-container {
      flex: 1;
      position: relative;
      background: #e8e8e8;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;

      .gen-progress-mask {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.65);
        z-index: 100;
        display: flex;
        align-items: center;
        justify-content: center;

        .progress-box {
          background: #fff;
          padding: 24px 32px;
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          width: 320px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);

          .progress-text {
            font-size: 14px;
            font-weight: 600;
            color: #333;
          }
        }
      }

      .preview-stage-scroll {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding: 20px 0;
        overflow-y: auto;
      }

      .phone-wrap {
        position: relative;
        display: flex;
        justify-content: center;
        margin: auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        border-radius: 36px;
      }

      .phone-scale {
        transform-origin: top center;
      }

      .phone {
        position: relative;
        overflow: hidden;
        background-color: var(--light-bg-color);
        user-select: none;
        border-radius: 40px;

        &.dark {
          background-color: var(--dark-bg-color);
        }

        .phone-bg {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: 0;
          .phone-bg-for-height {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }
      }

      .empty-preview {
        margin: auto;
        color: #999;
        font-size: 14px;
      }
    }

    .generated-gallery-bar {
      border-top: 1px solid var(--border-color);
      background: var(--bg-color);
      padding: 10px 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;

      .gallery-title {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        font-weight: 600;
        color: #666;
        .gallery-tip {
          font-size: 11px;
          font-weight: normal;
          color: #999;
        }
      }

      .gallery-items {
        display: flex;
        gap: 10px;
        overflow-x: auto;
        padding-bottom: 4px;

        .thumb-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px;
          cursor: pointer;
          padding: 4px;
          border-radius: 6px;
          border: 1px solid var(--border-color);
          background: #fafafa;
          transition: all 0.2s;

          &:hover {
            border-color: #fd6e6a;
            transform: translateY(-2px);
          }

          .thumb-img {
            width: 44px;
            height: 90px;
            object-fit: cover;
            border-radius: 4px;
          }

          .thumb-label {
            font-size: 10px;
            color: #666;
          }
        }
      }
    }
  }
}
</style>
