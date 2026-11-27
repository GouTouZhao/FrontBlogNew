<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import { useRouter } from 'vue-router';
import api, { refreshAccessToken } from '../api';
import { showToast } from '../utils/toast';

const router = useRouter();

// 鉴权与用户信息
const token = ref(localStorage.getItem('access_token') || '');
const userId = ref(localStorage.getItem('user_id') || '');
const nickname = ref(localStorage.getItem('user_nickname') || '我');
const isLoggedIn = computed(() => !!token.value && !!userId.value);

// 设备码逻辑：浏览器内持久保存
const getOrCreateDeviceId = () => {
  let did = localStorage.getItem('goutou_device_id');
  if (!did) {
    // 检查 cookie 兜底
    const match = document.cookie.match(/(?:^|;\s*)goutou_device_id=([^;]*)/);
    if (match && match[1]) {
      did = decodeURIComponent(match[1]);
    }
  }
  if (!did) {
    did = 'web_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now().toString(36);
    localStorage.setItem('goutou_device_id', did);
    document.cookie = `goutou_device_id=${encodeURIComponent(did)};path=/;max-age=${365 * 24 * 3600}`;
  }
  return did;
};

const deviceId = ref(getOrCreateDeviceId());

// 连接与校验状态（必须设备码上报与 WebSocket 连接成功才允许进入）
const isConnecting = ref(true);
const isConnected = ref(false);
const connectionError = ref('');

// WebSocket 对象
let socket = null;

// 会话管理
const conversations = ref([]);
const currentConvId = ref(0); // 0 为主会话（默认会话）
const showNewConvModal = ref(false);
const newConvTitle = ref('');

// 消息列表与输入框
const messages = ref([]);
const inputMessage = ref('');
const isSending = ref(false);
const messagesContainer = ref(null);

// ask_user 回复输入缓存
const askUserAnswers = ref({});
const submittingAskUser = ref({});

const getRequestBase = () => ({
  access_token: token.value,
  user_id: Number(userId.value) || 0
});

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 1. 初始化进入：设备码上传验证与 WebSocket 长连接建立
const initDeviceAndWebSocket = async (isRetry = false) => {
  if (!isLoggedIn.value) {
    isConnecting.value = false;
    connectionError.value = '请先登录 GouTou 账号后再进入助理。';
    return;
  }

  isConnecting.value = true;
  connectionError.value = '';

  try {
    // 步骤一：上报/验证设备码
    const regPayload = {
      base: getRequestBase(),
      device_id: deviceId.value,
      device_name: 'Web Browser (' + (navigator.userAgent.slice(0, 36)) + ')',
      platform: 'web',
      vendor: 'browser',
      is_active: true
    };

    const regRes = await api.post('/agent/register_device', regPayload);
    const isRegSuccess = regRes.data && (regRes.data.errCode === 0 || regRes.data.code === 0);
    if (!isRegSuccess) {
      throw new Error(regRes.data?.errMsg || regRes.data?.msg || '设备码注册/验证失败');
    }

    // 步骤二：建立 WebSocket 连接
    let apiBase = api.defaults.baseURL || window.location.origin;
    if (apiBase.startsWith('/')) {
      apiBase = window.location.origin + apiBase;
    }
    const wsBase = apiBase.replace(/^http/, 'ws');
    // 动态拉取最新的 access_token，防止静默刷新后仍使用旧 token 导致连接被拒绝
    token.value = localStorage.getItem('access_token') || '';
    const wsUrl = `${wsBase}/agent/ws?device_id=${encodeURIComponent(deviceId.value)}&token=${encodeURIComponent(token.value)}`;

    if (socket) {
      try { socket.close(); } catch (e) {}
    }

    socket = new WebSocket(wsUrl);

    socket.onopen = async () => {
      isConnected.value = true;
      isConnecting.value = false;
      connectionError.value = '';
      showToast('设备验证通过，WebSocket 已连通', 'success');
      // 成功进入应用后加载会话与历史消息
      await loadConversations();
      await loadHistoryMessages(currentConvId.value);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleIncomingMessage(data);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    socket.onerror = async (err) => {
      if (!isConnected.value) {
        // 如果握手失败且尚未重试过，尝试通过 7 天 RefreshToken 刷新凭据并重试
        if (!isRetry && localStorage.getItem('refresh_token')) {
          try {
            console.log('[WebSocket] 握手失败，尝试通过 RefreshToken 静默刷新凭据并重连...');
            await refreshAccessToken();
            await initDeviceAndWebSocket(true);
            return;
          } catch (rfErr) {
            console.error('[WebSocket] RefreshToken 刷新失败:', rfErr);
          }
        }
        isConnecting.value = false;
        connectionError.value = 'WebSocket 握手或长连接失败，未能进入 GouTou 助理，请检查网络或重新登录。';
      }
    };

    socket.onclose = () => {
      if (!isConnected.value) {
        isConnecting.value = false;
        connectionError.value = 'WebSocket 连接已关闭，未获准进入。';
      }
    };
  } catch (err) {
    isConnecting.value = false;
    connectionError.value = '设备验证失败: ' + (err.response?.data?.errMsg || err.response?.data?.msg || err.message || '网络连接异常');
  }
};

// 收到 WebSocket 推送消息
const handleIncomingMessage = (data) => {
  // 提取消息实体
  let msgObj = data;
  if (data.data) {
    msgObj = data.data;
  }

  const convId = Number(msgObj.conversation_id || 0);
  // 解析 metadata
  let meta = null;
  if (typeof msgObj.metadata === 'string' && msgObj.metadata) {
    try {
      meta = JSON.parse(msgObj.metadata);
    } catch (e) {}
  } else if (typeof msgObj.metadata === 'object') {
    meta = msgObj.metadata;
  }

  const incomingItem = {
    message_id: msgObj.message_id || Date.now(),
    conversation_id: convId,
    sequence: msgObj.sequence || 0,
    role: msgObj.role || 'assistant',
    content: msgObj.content || msgObj.message || '',
    metadata: meta,
    created_at: msgObj.created_at || Date.now() / 1000
  };

  // 若属于当前正在查看的会话，则追加展示
  if (convId === currentConvId.value) {
    const exists = messages.value.some(m => m.message_id && m.message_id === incomingItem.message_id);
    if (!exists) {
      messages.value.push(incomingItem);
      scrollToBottom();
    }
  }

  // 刷新当前会话列表活跃度
  const targetConv = conversations.value.find(c => c.conversation_id === convId);
  if (targetConv) {
    targetConv.max_seq = incomingItem.sequence;
  }
};

// 加载会话列表
const loadConversations = async () => {
  try {
    const res = await api.post('/agent/get_conversations', {
      base: getRequestBase(),
      limit: 50
    });
    if (res.data && (res.data.errCode === 0 || res.data.code === 0)) {
      const list = res.data.data?.conversations || [];
      // 保证主会话（ID = 0）置顶存在
      const hasMain = list.some(c => c.conversation_id === 0);
      if (!hasMain) {
        list.unshift({
          conversation_id: 0,
          title: '主会话',
          max_seq: 0,
          status: 'active'
        });
      }
      conversations.value = list;
    }
  } catch (e) {
    console.error('Failed to load conversations:', e);
  }
};

// 切换会话
const switchConversation = async (convId) => {
  if (currentConvId.value === convId) return;
  currentConvId.value = convId;
  await loadHistoryMessages(convId);
};

// 创建新子会话
const createNewConversation = async () => {
  const title = newConvTitle.value.trim() || '新的子对话';
  try {
    const res = await api.post('/agent/create_conversation', {
      base: getRequestBase(),
      title
    });
    if (res.data && (res.data.errCode === 0 || res.data.code === 0)) {
      showToast('创建会话成功', 'success');
      showNewConvModal.value = false;
      newConvTitle.value = '';
      await loadConversations();
      const newConv = res.data.data?.conversation;
      if (newConv) {
        await switchConversation(newConv.conversation_id);
      }
    } else {
      showToast(res.data?.errMsg || res.data?.msg || '创建会话失败', 'error');
    }
  } catch (e) {
    showToast('创建会话异常: ' + e.message, 'error');
  }
};

// 加载指定会话的历史记录
const loadHistoryMessages = async (convId) => {
  try {
    const res = await api.post('/agent/get_history_messages', {
      base: getRequestBase(),
      conversation_id: convId,
      from_sequence: 0,
      limit: 50,
      order_asc: false
    });
    if (res.data && (res.data.errCode === 0 || res.data.code === 0)) {
      const rawList = res.data.data?.messages || [];
      messages.value = rawList.map(m => {
        let meta = null;
        if (typeof m.metadata === 'string' && m.metadata) {
          try { meta = JSON.parse(m.metadata); } catch (e) {}
        } else if (typeof m.metadata === 'object') {
          meta = m.metadata;
        }
        return {
          ...m,
          metadata: meta
        };
      });
      scrollToBottom();
    }
  } catch (e) {
    console.error('Failed to load history messages:', e);
  }
};

// 发送常规用户消息
const sendMessage = async () => {
  const text = inputMessage.value.trim();
  if (!text || isSending.value) return;

  const tempUserMsg = {
    message_id: 'temp_' + Date.now(),
    conversation_id: currentConvId.value,
    role: 'user',
    content: text,
    created_at: Date.now() / 1000
  };
  messages.value.push(tempUserMsg);
  inputMessage.value = '';
  scrollToBottom();

  isSending.value = true;
  try {
    const res = await api.post('/agent/send_message', {
      base: getRequestBase(),
      message: text,
      conversation_id: currentConvId.value
    });
    if (res.data && (res.data.errCode === 0 || res.data.code === 0)) {
      if (res.data.data?.sequence) {
        tempUserMsg.sequence = res.data.data.sequence;
      }
    } else {
      showToast(res.data?.errMsg || res.data?.msg || '发送失败', 'error');
    }
  } catch (e) {
    showToast('发送消息异常: ' + (e.response?.data?.errMsg || e.response?.data?.msg || e.message), 'error');
  } finally {
    isSending.value = false;
  }
};

// ask_user 专属回复逻辑
const submitAskUserAnswer = async (msg) => {
  const taskId = msg.metadata?.task_id;
  const answer = (askUserAnswers.value[msg.message_id] || '').trim();
  if (!answer) {
    showToast('请输入回复内容', 'warning');
    return;
  }
  if (!taskId) {
    showToast('未找到关联任务 ID', 'error');
    return;
  }

  submittingAskUser.value[msg.message_id] = true;
  try {
    const res = await api.post('/agent/reply_ask_user', {
      base: getRequestBase(),
      task_id: taskId,
      answer
    });
    if (res.data && (res.data.errCode === 0 || res.data.code === 0)) {
      showToast('回复已提交给 Agent', 'success');
      // 记录在界面上已回答
      if (!msg.metadata) msg.metadata = {};
      msg.metadata.answered = true;
      msg.metadata.user_answer = answer;
      delete askUserAnswers.value[msg.message_id];
      // 将用户回答作为用户消息追加在下方
      messages.value.push({
        message_id: 'ans_' + Date.now(),
        conversation_id: currentConvId.value,
        role: 'user',
        content: answer,
        created_at: Date.now() / 1000
      });
      scrollToBottom();
    } else {
      showToast(res.data?.errMsg || res.data?.msg || '回复失败', 'error');
    }
  } catch (e) {
    showToast('提交回复异常: ' + e.message, 'error');
  } finally {
    submittingAskUser.value[msg.message_id] = false;
  }
};

// 判断是否为 ask_user 消息类型
const isAskUserMessage = (msg) => {
  if (!msg) return false;
  if (msg.metadata?.mode === 'ask_user') return true;
  if (msg.metadata?.action === 'ask_user') return true;
  if (msg.metadata?.question) return true;
  return false;
};

// 完成状态中的任务加载记录
const completingCron = ref({});

// 判断是否为 cron 定时提醒消息类型
const isCronReminderMessage = (msg) => {
  if (!msg) return false;
  const meta = msg.metadata;
  if (!meta) return false;
  return meta.mode === 'cron' || meta.type === 'cron_reminder' || !!meta.cron_id;
};

// 提交标记定时提醒任务已完成
const submitCompleteCron = async (msg) => {
  const cronId = msg.metadata?.cron_id;
  if (!cronId) {
    showToast('未找到对应的提醒任务 ID', 'error');
    return;
  }

  completingCron.value[cronId] = true;
  try {
    const res = await api.post('/agent/complete_cron', {
      base: getRequestBase(),
      cron_id: cronId,
      message_id: msg.message_id
    });
    if (res.data && (res.data.errCode === 0 || res.data.code === 0)) {
      showToast('任务已标记完成，后续不再提醒', 'success');
      if (!msg.metadata) msg.metadata = {};
      msg.metadata.completed = true;
    } else {
      showToast(res.data?.errMsg || res.data?.msg || '操作失败', 'error');
    }
  } catch (e) {
    showToast('标记完成异常: ' + e.message, 'error');
  } finally {
    completingCron.value[cronId] = false;
  }
};

onMounted(() => {
  initDeviceAndWebSocket();
});

onUnmounted(() => {
  if (socket) {
    try { socket.close(); } catch (e) {}
    socket = null;
  }
});
</script>

<template>
  <div class="assistant-container">
    <!-- 1. 连接与验证拦截层（未成功建立则阻断进入） -->
    <div v-if="!isConnected" class="gate-overlay">
      <div class="gate-card">
        <div class="gate-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a2 2 0 0 1 2 2v2a8 8 0 0 1 7.938 7H22a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-1.07A8.001 8.001 0 0 1 14 22H10a8.001 8.001 0 0 1-6.93-4H2a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1h1.062A8 8 0 0 1 10 6V4a2 2 0 0 1 2-2zm-3 10a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm6 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z" />
          </svg>
        </div>
        <h2 class="gate-title">GouTou 助理设备验证</h2>
        
        <div v-if="isConnecting" class="gate-status connecting">
          <div class="spinner"></div>
          <p>正在上报设备码并建立 WebSocket 长连接通道...</p>
          <span class="device-tag">设备码: {{ deviceId }}</span>
        </div>

        <div v-else-if="connectionError" class="gate-status error">
          <p class="error-msg">{{ connectionError }}</p>
          <div class="gate-actions">
            <button class="retry-btn" @click="initDeviceAndWebSocket">重新验证与连接</button>
            <button class="back-btn" @click="router.push('/apps')">返回应用中心</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 正常聊天主界面（验证通过后渲染） -->
    <div v-else class="chat-main-layout">
      <!-- 左侧：会话列表 -->
      <aside class="conv-sidebar">
        <div class="conv-header">
          <h3>会话列表</h3>
          <button class="new-conv-btn" @click="showNewConvModal = true" title="创建子会话">+</button>
        </div>
        <div class="conv-list">
          <div
            v-for="c in conversations"
            :key="c.conversation_id"
            class="conv-item"
            :class="{ active: currentConvId === c.conversation_id }"
            @click="switchConversation(c.conversation_id)"
          >
            <span class="conv-tag" v-if="c.conversation_id === 0">主会话</span>
            <span class="conv-tag sub" v-else>子会话</span>
            <span class="conv-title">{{ c.title || '会话 ' + c.conversation_id }}</span>
          </div>
        </div>
      </aside>

      <!-- 右侧：对话主窗格 -->
      <main class="chat-pane">
        <!-- 窗格顶部栏 -->
        <header class="pane-header">
          <div class="pane-title">
            <strong>GouTou 助理</strong>
            <span class="conv-badge" v-if="currentConvId === 0">主会话 (默认)</span>
            <span class="conv-badge sub" v-else>子会话 #{{ currentConvId }}</span>
          </div>
          <div class="pane-actions">
            <button class="icon-btn" @click="router.push('/apps')">返回应用中心</button>
          </div>
        </header>

        <!-- 消息历史流 -->
        <div class="messages-stream" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-hint">
            <p>暂无消息，向 GouTou 助理发送一句话开始对话吧！</p>
          </div>

          <div
            v-for="msg in messages"
            :key="msg.message_id || msg.sequence"
            class="msg-row"
            :class="msg.role === 'user' ? 'msg-user' : 'msg-assistant'"
          >
            <!-- 普通用户气泡 -->
            <div v-if="msg.role === 'user'" class="bubble user-bubble">
              <div class="bubble-content">{{ msg.content }}</div>
            </div>

            <!-- Agent 消息 -->
            <div v-else class="bubble-container">
              <!-- 特殊展示：ask_user 专属卡片 -->
              <div v-if="isAskUserMessage(msg)" class="ask-user-card">
                <div class="ask-header">
                  <span class="ask-badge">助理追问 / 待补充</span>
                  <span class="ask-prompt">请回答以下问题以便继续执行任务：</span>
                </div>
                <div class="ask-question">{{ msg.metadata?.question || msg.content }}</div>
                
                <!-- 已回复状态展示 -->
                <div v-if="msg.metadata?.answered" class="answered-badge">
                  <span>✓ 已回复: {{ msg.metadata?.user_answer }}</span>
                </div>

                <!-- 专属下方自带输入框 -->
                <div v-else class="ask-input-box">
                  <input
                    type="text"
                    v-model="askUserAnswers[msg.message_id]"
                    placeholder="针对此追问输入您的回复..."
                    @keyup.enter="submitAskUserAnswer(msg)"
                    :disabled="submittingAskUser[msg.message_id]"
                  />
                  <button
                    class="ask-reply-btn"
                    @click="submitAskUserAnswer(msg)"
                    :disabled="submittingAskUser[msg.message_id]"
                  >
                    {{ submittingAskUser[msg.message_id] ? '提交中...' : '提交回复' }}
                  </button>
                </div>
              </div>

              <!-- 特殊展示：cron 定时提醒专属卡片 -->
              <div v-else-if="isCronReminderMessage(msg)" class="cron-reminder-card">
                <div class="cron-header">
                  <span class="cron-badge">⏰ 计划提醒</span>
                  <span v-if="msg.metadata?.target_at" class="cron-target-time">目标时间: {{ msg.metadata.target_at }}</span>
                </div>
                <div class="cron-content">{{ msg.content }}</div>
                
                <div class="cron-actions">
                  <!-- 已完成状态展示 -->
                  <div v-if="msg.metadata?.completed" class="cron-completed-badge">
                    <span>✓ 已完成 (已终止后续提醒)</span>
                  </div>
                  <!-- 未完成：已完成按钮 -->
                  <button
                    v-else
                    class="cron-complete-btn"
                    @click="submitCompleteCron(msg)"
                    :disabled="completingCron[msg.metadata?.cron_id]"
                  >
                    {{ completingCron[msg.metadata?.cron_id] ? '正在处理...' : '✓ 已完成 (不再提醒)' }}
                  </button>
                </div>
              </div>

              <!-- 普通 Agent 消息气泡 -->
              <div v-else class="bubble assistant-bubble">
                <div class="bubble-content">{{ msg.content }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部消息输入区域 -->
        <footer class="input-footer">
          <input
            type="text"
            v-model="inputMessage"
            placeholder="输入您的问题或指令..."
            @keyup.enter="sendMessage"
            :disabled="isSending"
          />
          <button class="send-btn" @click="sendMessage" :disabled="isSending || !inputMessage.trim()">
            {{ isSending ? '发送中...' : '发送' }}
          </button>
        </footer>
      </main>
    </div>

    <!-- 创建子会话模态框 -->
    <div v-if="showNewConvModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>创建新会话（子会话）</h3>
        <p class="modal-desc">为新的协同对话起一个标题：</p>
        <input
          type="text"
          v-model="newConvTitle"
          placeholder="例如：论文校对、代码分析"
          @keyup.enter="createNewConversation"
        />
        <div class="modal-btns">
          <button class="cancel-btn" @click="showNewConvModal = false">取消</button>
          <button class="confirm-btn" @click="createNewConversation">创建并进入</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.assistant-container {
  max-width: 1200px;
  height: calc(100vh - 100px);
  margin: 20px auto;
  padding: 0 16px;
  box-sizing: border-box;
}

/* 1. 验证拦截门禁 */
.gate-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.gate-card {
  background: var(--bg-color, #ffffff);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 16px;
  padding: 40px;
  max-width: 480px;
  width: 100%;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
}

.gate-icon svg {
  width: 56px;
  height: 56px;
  stroke: var(--text-color, #333333);
}

.gate-title {
  margin: 20px 0 10px;
  font-size: 22px;
  color: var(--text-color, #333333);
}

.gate-status {
  margin-top: 24px;
}

.device-tag {
  display: inline-block;
  margin-top: 12px;
  padding: 4px 10px;
  background: rgba(128, 128, 128, 0.1);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-color, #666666);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(128, 128, 128, 0.2);
  border-top-color: var(--text-color, #333333);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-msg {
  color: #ff4d4f;
  margin-bottom: 20px;
  font-size: 14px;
}

.gate-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.retry-btn, .confirm-btn, .send-btn {
  background: var(--text-color, #222);
  color: var(--bg-color, #fff);
  border: none;
  padding: 8px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

.retry-btn:hover, .confirm-btn:hover, .send-btn:hover {
  opacity: 0.85;
}

.back-btn, .cancel-btn {
  background: transparent;
  border: 1px solid var(--border-color, #ccc);
  color: var(--text-color, #333);
  padding: 8px 18px;
  border-radius: 8px;
  cursor: pointer;
}

/* 2. 聊天主界面布局 */
.chat-main-layout {
  display: flex;
  height: 100%;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 16px;
  overflow: hidden;
  background: var(--bg-color, #ffffff);
}

/* 会话列表侧栏 */
.conv-sidebar {
  width: 260px;
  border-right: 1px solid var(--border-color, #e0e0e0);
  display: flex;
  flex-direction: column;
  background: rgba(128, 128, 128, 0.03);
}

.conv-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.conv-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-color);
}

.new-conv-btn {
  background: var(--text-color, #222);
  color: var(--bg-color, #fff);
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.15s;
}

.conv-item:hover {
  background: rgba(128, 128, 128, 0.08);
}

.conv-item.active {
  background: rgba(128, 128, 128, 0.15);
  font-weight: 600;
}

.conv-tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--text-color);
  color: var(--bg-color);
}

.conv-tag.sub {
  background: rgba(128, 128, 128, 0.2);
  color: var(--text-color);
}

.conv-title {
  flex: 1;
  font-size: 14px;
  color: var(--text-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 对话主窗格 */
.chat-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.pane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.pane-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-color);
}

.conv-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  color: var(--text-color);
}

.icon-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}

/* 消息流 */
.messages-stream {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-hint {
  text-align: center;
  color: rgba(128, 128, 128, 0.7);
  margin-top: 60px;
}

.msg-row {
  display: flex;
  width: 100%;
}

.msg-user {
  justify-content: flex-end;
}

.msg-assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.user-bubble {
  background: var(--text-color, #222);
  color: var(--bg-color, #fff);
  border-bottom-right-radius: 2px;
}

.assistant-bubble {
  background: rgba(128, 128, 128, 0.08);
  border: 1px solid var(--border-color, #e0e0e0);
  color: var(--text-color, #333);
  border-bottom-left-radius: 2px;
}

/* ask_user 专属卡片式展示与下方输入框 */
.ask-user-card {
  max-width: 80%;
  background: rgba(255, 165, 0, 0.05);
  border: 1px solid rgba(255, 165, 0, 0.4);
  border-radius: 12px;
  padding: 16px;
  color: var(--text-color);
}

.ask-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.ask-badge {
  background: #faad14;
  color: #fff;
  font-size: 11px;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}

.ask-prompt {
  font-size: 12px;
  opacity: 0.8;
}

.ask-question {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 14px;
}

.ask-input-box {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.ask-input-box input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 6px;
  background: var(--bg-color);
  color: var(--text-color);
  font-size: 13px;
}

.ask-reply-btn {
  background: #faad14;
  color: #fff;
  border: none;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
}

.answered-badge {
  color: #52c41a;
  font-size: 13px;
  margin-top: 6px;
}

/* cron 定时提醒专属卡片式展示 */
.cron-reminder-card {
  max-width: 80%;
  background: rgba(82, 196, 26, 0.05);
  border: 1px solid rgba(82, 196, 26, 0.4);
  border-radius: 12px;
  padding: 16px;
  color: var(--text-color);
}

.cron-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.cron-badge {
  background: #52c41a;
  color: #fff;
  font-size: 11px;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}

.cron-target-time {
  font-size: 12px;
  opacity: 0.75;
}

.cron-content {
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  margin-bottom: 12px;
}

.cron-actions {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.cron-complete-btn {
  background: var(--text-color, #222);
  color: var(--bg-color, #fff);
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: opacity 0.2s;
}

.cron-complete-btn:hover:not(:disabled) {
  opacity: 0.85;
}

.cron-complete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cron-completed-badge {
  color: #52c41a;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 底部通用输入条 */
.input-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color, #e0e0e0);
  background: var(--bg-color);
}

.input-footer input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  background: var(--bg-color);
  color: var(--text-color);
  font-size: 14px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  width: 360px;
}

.modal-card h3 {
  margin: 0 0 10px;
  color: var(--text-color);
}

.modal-desc {
  font-size: 13px;
  opacity: 0.7;
  margin-bottom: 12px;
  color: var(--text-color);
}

.modal-card input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-color);
  color: var(--text-color);
  box-sizing: border-box;
  margin-bottom: 16px;
}

.modal-btns {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 768px) {
  .chat-main-layout {
    flex-direction: column;
  }
  .conv-sidebar {
    width: 100%;
    height: 140px;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }
}
</style>