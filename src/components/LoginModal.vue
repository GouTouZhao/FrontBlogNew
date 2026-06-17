<script setup>
import { ref } from 'vue';
import api from '../api';
import { showToast } from '../utils/toast';

const props = defineProps({
  isVisible: Boolean
});

const emit = defineEmits(['close', 'loginSuccess']);

const isLogin = ref(true);
const form = ref({
  email: '',
  password: ''
});

const loading = ref(false);
const errorMsg = ref('');

const close = () => {
  emit('close');
  errorMsg.value = '';
  form.value.password = '';
};

const toggleMode = () => {
  isLogin.value = !isLogin.value;
  errorMsg.value = '';
  form.value.password = '';
};

const handleSubmit = async () => {
  if (!form.value.email || !form.value.password) {
    errorMsg.value = '邮箱和密码不能为空';
    return;
  }
  
  loading.value = true;
  errorMsg.value = '';

  try {
    const endpoint = isLogin.value ? '/user/user_login' : '/user/user_register';
    const response = await api.post(endpoint, {
      email: form.value.email,
      password: form.value.password
    });
    
    const res = response.data;
    
    let data = res;
    if (res.errCode === 0 && res.data) {
      data = res.data;
    }

    const token = data.accessToken || data.access_token;
    const refreshToken = data.refreshToken || data.refresh_token;
    const userEmail = data.email;
    const userId = data.userId || data.user_id;
    const userNickname = data.nickname;

    if (token) {
      localStorage.setItem('access_token', token);
      localStorage.setItem('refresh_token', refreshToken);
      localStorage.setItem('user_email', userEmail || form.value.email);
      localStorage.setItem('user_nickname', userNickname || '新用户');
      localStorage.setItem('user_id', userId || '');
      
      showToast(isLogin.value ? '登录成功' : '注册成功', 'success');
      emit('loginSuccess');
      close();
    } else {
       errorMsg.value = res.errMsg || '服务器响应异常';
    }

  } catch (error) {
    if (error.response && error.response.data && error.response.data.errMsg) {
      errorMsg.value = error.response.data.errMsg;
    } else if (error.response && error.response.data && error.response.data.message) {
      errorMsg.value = error.response.data.message;
    } else {
      errorMsg.value = isLogin.value ? '登录失败，请检查邮箱或密码' : '注册失败，请稍后再试';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <transition name="modal">
    <div v-if="isVisible" class="modal-overlay" @click.self="close">
      <div class="modal-card card">
        <button class="close-btn" @click="close">&times;</button>
        <h2 class="auth-title">{{ isLogin ? '登录' : '创建账号' }}</h2>
        
        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="input-group">
            <label>邮箱</label>
            <input 
              type="email" 
              v-model="form.email" 
              placeholder="输入您的邮箱" 
              required 
            />
          </div>
          
          <div class="input-group">
            <label>密码</label>
            <input 
              type="password" 
              v-model="form.password" 
              placeholder="输入密码" 
              required 
            />
          </div>
          
          <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>
          
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </form>
        
        <div class="auth-switch">
          <span class="switch-text">{{ isLogin ? '没有账号？' : '已有账号？' }}</span>
          <button class="switch-btn" @click="toggleMode" type="button">
            {{ isLogin ? '立即注册' : '返回登录' }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-card {
  position: relative;
  width: 100%;
  max-width: 400px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  font-size: 28px;
  line-height: 1;
  color: var(--card-text);
  opacity: 0.5;
  cursor: pointer;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

.auth-title {
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 14px;
  font-weight: 600;
  opacity: 0.8;
}

.input-group input {
  background: var(--bg-color);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-color);
  padding: 12px 16px;
  font-size: 16px;
  outline: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.input-group input:focus {
  border-color: var(--text-color);
  box-shadow: 0 0 0 2px var(--glass-border), 0 8px 16px rgba(0, 0, 0, 0.1);
}

.input-group input::placeholder {
  color: var(--text-color);
  opacity: 0.5;
}

.error-message {
  color: #ff4d4f;
  font-size: 13px;
  text-align: center;
  margin-top: -8px;
}

.submit-btn {
  background: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--glass-border);
  padding: 12px 48px;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 16px;
  margin: 16px auto 0;
  min-width: 160px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px var(--glass-shadow);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.auth-switch {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  margin-top: 16px;
}

.switch-text {
  opacity: 0.6;
}

.switch-btn {
  font-weight: 700;
  text-decoration: underline;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.switch-btn:hover {
  opacity: 1;
}

/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-card,
.modal-leave-active .modal-card {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-card,
.modal-leave-to .modal-card {
  transform: scale(0.95) translateY(20px);
}
</style>
