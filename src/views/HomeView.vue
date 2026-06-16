<script setup>
import { onMounted, onUnmounted } from 'vue';
import { partitions } from '../data/mock';
import { useRouter } from 'vue-router';

const router = useRouter();

const goToPartition = (id) => {
  router.push(`/${id}`);
};

let observer;
const initObserver = () => {
  if (observer) observer.disconnect();
  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  });

  const elements = document.querySelectorAll('.reveal');
  elements.forEach((el) => observer.observe(el));
};

onMounted(() => {
  initObserver();
});

onUnmounted(() => {
  if (observer) observer.disconnect();
});
</script>

<template>
  <div class="home-view">
    <section class="hero">
      <h1 class="reveal delay-100">极简主义是极致的复杂。</h1>
      <p class="reveal delay-200 subtitle">透过现代化的视角，探索摄影、技术与生活。</p>
    </section>

    <section class="categories" id="categories">
      <h2 class="reveal delay-100 section-title">分区</h2>
      <div class="grid">
        <div class="card reveal" :class="'delay-' + ((index % 3 + 1) * 100)" v-for="(p, index) in partitions" :key="p.id" @click="goToPartition(p.id)">
          <h3>{{ p.name }}</h3>
          <p>{{ p.desc }}</p>
        </div>
      </div>
    </section>

    <section class="recent-posts reveal delay-200">
      <h2 class="section-title">最新动态</h2>
      <div class="post-list">
        <article class="post-item" v-for="i in 3" :key="i">
          <div class="post-meta">全站速递 • 刚才</div>
          <h3 class="post-title">欢迎来到全新的简约空间</h3>
          <p class="post-excerpt">摒弃繁杂，带来更好的用户体验。极简是追求内心的平静与专注...</p>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-bottom: 80px;
  max-width: 800px;
}

.hero h1 {
  font-size: 5rem;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -2px;
  margin-bottom: 24px;
}

.subtitle {
  font-size: 1.5rem;
  opacity: 0.7;
  font-weight: 400;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 40px;
  letter-spacing: -1px;
}

.categories {
  margin-bottom: 120px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 32px;
}

.card {
  cursor: pointer;
}

.card h3 {
  font-size: 1.5rem;
  margin-bottom: 12px;
  font-weight: 600;
}

.card p {
  opacity: 0.8;
  font-size: 1rem;
}

.recent-posts {
  max-width: 800px;
  margin-bottom: 80px;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.post-item {
  padding-bottom: 40px;
  border-bottom: 1px solid var(--border-color);
}

.post-item:last-child {
  border-bottom: none;
}

.post-meta {
  font-size: 0.875rem;
  opacity: 0.6;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.post-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
  cursor: pointer;
}

.post-title:hover {
  text-decoration: underline;
}

.post-excerpt {
  font-size: 1.125rem;
  opacity: 0.8;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 3.5rem;
  }
}
</style>
