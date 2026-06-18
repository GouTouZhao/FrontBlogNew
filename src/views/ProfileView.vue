<script setup>
import { reactive, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { showToast } from '../utils/toast';

const router = useRouter();

const state = reactive({
  ctrlV: '',
  showAvatar: false,
  name: '',
  wechatLabel: '',
  wechatValue: '',
  emailLabel: '',
  emailValue: '',
  desc: ''
});

const isEditingName = ref(false);
const editingNameValue = ref('');

const currentUser = ref(null);
const cursorAt = ref('ctrlV');

const sequence = [
  { key: 'ctrlV', text: 'Ctrl+V', delayAfter: 400 },
  { action: () => { state.ctrlV = ''; state.showAvatar = true; cursorAt.value = 'name'; }, delayAfter: 500 },
  { key: 'name', text: 'GouTou', delayAfter: 300 },
  { action: () => { cursorAt.value = 'wechatLabel'; } },
  { key: 'wechatLabel', text: '微信', delayAfter: 200 },
  { action: () => { cursorAt.value = 'wechatValue'; } },
  { key: 'wechatValue', text: 'goutouspare', delayAfter: 300 },
  { action: () => { cursorAt.value = 'emailLabel'; } },
  { key: 'emailLabel', text: '邮箱', delayAfter: 200 },
  { action: () => { cursorAt.value = 'emailValue'; } },
  { key: 'emailValue', text: '3057907836@qq.com', delayAfter: 300 },
  { action: () => { cursorAt.value = 'desc'; } },
  { key: 'desc', text: 'SYSU，在这里分享我的创意和生活', delayAfter: 0 }
];

const startTypingSequence = async () => {
  for (const step of sequence) {
    if (step.action) {
      step.action();
    }
    if (step.key && step.text) {
      cursorAt.value = step.key;
      for (let i = 0; i < step.text.length; i++) {
        state[step.key] += step.text[i];
        await new Promise(r => setTimeout(r, 100)); // 100ms per character
      }
    }
    if (step.delayAfter) {
      await new Promise(r => setTimeout(r, step.delayAfter));
    }
  }
};

const checkAuth = () => {
  const token = localStorage.getItem('access_token');
  if (token) {
    currentUser.value = {
      id: localStorage.getItem('user_id'),
      email: localStorage.getItem('user_email'),
      nickname: localStorage.getItem('user_nickname'),
      token: token
    };
  }
};

const handleEditName = () => {
  isEditingName.value = true;
  editingNameValue.value = currentUser.value.nickname;
};

const saveName = async () => {
  if (!editingNameValue.value.trim()) {
    showToast('名称不能为空', 'warning');
    return;
  }
  
  try {
    await api.post('/user/update_user_info', {
      base: {
        access_token: currentUser.value.token,
        email: currentUser.value.email,
        user_id: parseInt(currentUser.value.id)
      },
      nick_name: editingNameValue.value
    });
    
    // Update local storage and current user
    localStorage.setItem('user_nickname', editingNameValue.value);
    currentUser.value.nickname = editingNameValue.value;
    isEditingName.value = false;
    showToast('名称修改成功', 'success');
  } catch (error) {
    console.error(error);
    showToast('修改名称失败', 'error');
  }
};

onMounted(() => {
  checkAuth();
  if (currentUser.value) {
    // If logged in, skip typing animation and show user data
    state.showAvatar = true;
    state.name = currentUser.value.nickname;
    state.wechatLabel = '微信';
    state.wechatValue = '未绑定';
    state.emailLabel = '邮箱';
    state.emailValue = currentUser.value.email;
    state.desc = '欢迎来到你的个人中心';
    cursorAt.value = ''; // Remove cursor
  } else {
    setTimeout(() => {
      startTypingSequence();
    }, 500);
  }
});
</script>

<template>
  <div class="profile-fullscreen">
    <div class="profile-content">
      <div class="profile-card">
        
        <div class="avatar-container">
          <span v-if="!state.showAvatar" class="typed-text">{{ state.ctrlV }}<span v-if="cursorAt === 'ctrlV'" class="cursor">|</span></span>
          <div v-else class="avatar-wrapper">
             <img v-if="!currentUser" src="../assets/GouTou.jpg" alt="GouTou Avatar" class="avatar-large" />
             <div v-else class="avatar-text-large">{{ currentUser.nickname.charAt(0).toUpperCase() }}</div>
          </div>
        </div>
        
        <div class="name-container">
          <h1 v-if="!isEditingName" class="name">
            <span class="typed-text">{{ currentUser ? currentUser.nickname : state.name }}</span>
            <span v-if="cursorAt === 'name'" class="cursor">|</span>
            <button v-if="currentUser" class="edit-btn" @click="handleEditName">修改</button>
          </h1>
          <div v-else class="name-edit">
            <input type="text" v-model="editingNameValue" class="edit-input" />
            <button class="save-btn" @click="saveName">保存</button>
            <button class="cancel-btn" @click="isEditingName = false">取消</button>
          </div>
        </div>
        
        <div class="contact-info">
          <div class="info-item">
            <span class="label">
              <span class="typed-text">{{ state.wechatLabel }}</span><span v-if="cursorAt === 'wechatLabel'" class="cursor">|</span>
            </span>
            <span class="value">
              <span class="typed-text">{{ state.wechatValue }}</span><span v-if="cursorAt === 'wechatValue'" class="cursor">|</span>
            </span>
          </div>
          <div class="info-item">
            <span class="label">
              <span class="typed-text">{{ state.emailLabel }}</span><span v-if="cursorAt === 'emailLabel'" class="cursor">|</span>
            </span>
            <span class="value">
              <span class="typed-text">{{ state.emailValue }}</span><span v-if="cursorAt === 'emailValue'" class="cursor">|</span>
            </span>
          </div>
        </div>

        <div class="description-container">
          <span class="typed-text">{{ state.desc }}</span><span v-if="cursorAt === 'desc'" class="cursor">|</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 100;
  background-color: var(--bg-color);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-content {
  position: relative;
  z-index: 10;
  color: var(--text-color);
}

.profile-card {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
}

.avatar-container {
  width: 120px;
  height: 120px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.avatar-wrapper {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  animation: fadeIn 0.5s ease-out forwards;
}

.avatar-large {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--text-color);
}

.avatar-text-large {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--text-color);
  color: var(--bg-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 800;
  text-transform: uppercase;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

.name-container {
  margin-bottom: 30px;
  min-height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.name {
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: -1px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.edit-btn {
  font-size: 1rem;
  background: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 4px 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: normal;
}

.edit-btn:hover {
  background: var(--border-color);
}

.name-edit {
  display: flex;
  gap: 12px;
  align-items: center;
}

.edit-input {
  font-size: 2rem;
  font-weight: 800;
  padding: 8px 16px;
  border-radius: 8px;
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-color);
  width: 200px;
  text-align: center;
}

.edit-input:focus {
  outline: none;
  border-color: var(--text-color);
}

.save-btn, .cancel-btn {
  font-size: 1rem;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  border: none;
}

.save-btn {
  background: var(--text-color);
  color: var(--bg-color);
}

.cancel-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 40px;
}

.info-item {
  font-size: 1.25rem;
  display: flex;
  gap: 16px;
  align-items: center;
  min-height: 1.5rem;
  justify-content: center;
}

.label {
  font-weight: 700;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.875rem;
  width: 60px;
  text-align: right;
  display: inline-block;
}

.value {
  font-weight: 500;
  text-align: left;
  width: 220px;
}

.description-container {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.5px;
  opacity: 0.9;
  max-width: 400px;
  line-height: 1.5;
  min-height: 2.25rem;
}

.cursor {
  display: inline-block;
  font-weight: 400;
  animation: blink 1s step-end infinite;
  margin-left: 2px;
  color: var(--text-color);
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
