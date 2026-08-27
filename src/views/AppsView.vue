<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isAdmin = computed(() => localStorage.getItem('user_email') === '2460607806@qq.com');

const apps = computed(() => {
  const list = [
    {
      id: 'exam-generator',
      path: '/apps/exam-generator',
      name: '生成试卷助手',
      description: '上传课件或文档，智能提取重点内容并自动生成相关试卷。',
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
    }
  ];

  if (isAdmin.value) {
    list.push({
      id: 'course-admin',
      path: '/admin/course',
      name: '课程申请审核',
      description: '管理员专属：审核用户发起的新增课程申请，管理课程库。',
      icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01'
    });
  }
  return list;
});

const goToApp = (path) => {
  router.push(path);
};
</script>

<template>
  <div class="apps-container">
    <div class="apps-header">
      <h1 class="apps-title">创意应用中心</h1>
      <p class="apps-subtitle">发现更多强大的智能工具，助力您的学习与工作</p>
    </div>

    <div class="apps-grid">
      <div v-for="app in apps" :key="app.id" class="app-card" @click="goToApp(app.path)">
        <div class="app-icon-container">
          <svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path :d="app.icon"></path>
          </svg>
        </div>
        <h3 class="app-name">{{ app.name }}</h3>
        <p class="app-desc">{{ app.description }}</p>
        <div class="app-card-footer">
          <span>立即使用</span>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.apps-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

.apps-header {
  margin-bottom: 40px;
  text-align: center;
}

.apps-title {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 12px;
  color: var(--text-color);
}

.apps-subtitle {
  font-size: 16px;
  opacity: 0.7;
  color: var(--text-color);
}

.apps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.app-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.app-card:hover {
  transform: translateY(-4px);
  border-color: var(--text-color);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.app-icon-container {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(128, 128, 128, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  color: var(--text-color);
}

.app-icon {
  width: 24px;
  height: 24px;
}

.app-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-color);
}

.app-desc {
  font-size: 14px;
  opacity: 0.7;
  color: var(--text-color);
  line-height: 1.5;
  flex-grow: 1;
  margin-bottom: 24px;
}

.app-card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  opacity: 0.8;
  transition: opacity 0.2s;
}

.app-card:hover .app-card-footer {
  opacity: 1;
}

@media (max-width: 640px) {
  .apps-title {
    font-size: 24px;
  }
  .apps-grid {
    grid-template-columns: 1fr;
  }
}
</style>
