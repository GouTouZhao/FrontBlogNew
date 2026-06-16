<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { partitions } from './data/mock';
import { 
  currentPartition,
  currentPage,
  paginatedList,
  hasPrevPage,
  hasNextPage,
  isEmpty,
  prevPage as storePrevPage,
  nextPage as storeNextPage
} from './store';

const router = useRouter();
const route = useRoute();

const isDark = ref(false);
const isSidebarExpanded = ref(false);

const toggleTheme = () => {
  isDark.value = !isDark.value;
  if (isDark.value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

const toggleSidebar = () => {
  isSidebarExpanded.value = !isSidebarExpanded.value;
};

const goToPartition = (id) => {
  router.push(`/${id}`);
};

const goHome = () => {
  router.push('/');
};

const goToProfile = () => {
  router.push('/profile');
};

const prevPage = async () => {
  if (hasPrevPage.value) {
    storePrevPage();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const nextPage = async () => {
  if (hasNextPage.value) {
    storeNextPage();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};
</script>

<template>
  <div class="app-container">
    <aside class="sidebar" :class="{ 'expanded': isSidebarExpanded, 'collapsed': !isSidebarExpanded }">
      <div class="sidebar-top">
        <button class="nav-toggle" @click="toggleSidebar">
          {{ isSidebarExpanded ? '收起' : '菜单' }}
        </button>
        <button v-if="isSidebarExpanded" class="theme-toggle" @click="toggleTheme">
          {{ isDark ? '日间模式' : '夜间模式' }}
        </button>

        <div v-if="isSidebarExpanded" class="profile-link" @click="goToProfile">
          <img src="./assets/GouTou.jpg" alt="GouTou" class="avatar-small" />
          <span class="profile-name">GouTou</span>
        </div>
      </div>

      <nav v-if="isSidebarExpanded" class="sidebar-middle">
        <ul class="nav-links">
          <li @click="goHome" :class="{ active: route.path === '/' }">
            <span class="nav-text">首页</span>
          </li>
          <li v-for="p in partitions" :key="p.id" @click="goToPartition(p.id)" :class="{ active: route.params.partition === p.id }">
            <span class="nav-text">{{ p.name }}</span>
          </li>
        </ul>

        <div v-if="currentPartition" class="sidebar-list">
          <div class="sidebar-divider"></div>
          
          <div class="sidebar-pagination-btn" v-if="hasPrevPage" @click="prevPage">
            ......
          </div>

          <ul class="sidebar-blog-links">
            <li v-if="isEmpty" class="sidebar-empty">无内容</li>
            <li v-for="item in paginatedList" :key="item.id" class="sidebar-blog-item">
              {{ item.title }}
            </li>
          </ul>

          <div class="sidebar-pagination-btn" v-if="hasNextPage" @click="nextPage">
            ......
          </div>
        </div>
      </nav>

      <div v-if="isSidebarExpanded" class="sidebar-bottom">
        <div class="user-info">
          <div class="avatar-text">用</div>
          <div class="user-details">
            <span class="user-name">游客</span>
            <span class="user-action">登录 / 注册</span>
          </div>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<style scoped>
.sidebar {
  padding: 20px 0;
  justify-content: space-between;
}

.sidebar-top {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 0 20px;
  align-items: flex-start;
}

.nav-toggle {
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 14px;
}

.theme-toggle {
  font-size: 14px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.theme-toggle:hover {
  opacity: 1;
}

.profile-link {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.2s;
  width: 100%;
}

.profile-link:hover {
  background-color: var(--border-color);
}

.avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--bg-color);
}

.profile-name {
  font-weight: 700;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.sidebar-middle {
  padding: 0 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-top: 40px;
  overflow-y: auto;
}

.nav-links {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.nav-links li {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.5px;
  opacity: 0.6;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
  display: inline-block;
}

.nav-links li:hover, .nav-links li.active {
  opacity: 1;
  transform: translateX(8px);
}

.sidebar-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sidebar-divider {
  height: 1px;
  background-color: var(--border-color);
  width: 100%;
  margin-bottom: 8px;
}

.sidebar-pagination-btn {
  font-size: 14px;
  font-weight: 700;
  text-align: center;
  cursor: pointer;
  opacity: 0.5;
  letter-spacing: 2px;
  padding: 4px 0;
  transition: opacity 0.2s;
}

.sidebar-pagination-btn:hover {
  opacity: 1;
}

.sidebar-blog-links {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0;
  margin: 0;
}

.sidebar-blog-item, .sidebar-empty {
  font-size: 13px;
  font-weight: 500;
  opacity: 0.7;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: opacity 0.2s;
}

.sidebar-blog-item:hover {
  opacity: 1;
  text-decoration: underline;
}

.sidebar-bottom {
  padding: 0 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.avatar-text {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--text-color);
  color: var(--bg-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
}

.user-action {
  font-size: 12px;
  opacity: 0.6;
  cursor: pointer;
}

.user-action:hover {
  opacity: 1;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .main-content {
    padding: 20px;
    margin-left: 60px;
  }
}
</style>

