export const partitions = [
  { id: 'photography', name: '摄影', desc: '在黑白与色彩之间捕捉瞬间。', path: '/photography' },
  { id: 'technology', name: '技术', desc: '深入探讨代码、架构与未来。', path: '/technology' },
  { id: 'life', name: '生活', desc: '反思、故事与日常感悟。', path: '/life' },
  { id: 'forum', name: '论坛', desc: '加入社区，参与热烈讨论。', path: '/forum' }
];

export const generateMockData = () => {
  const data = {};
  partitions.forEach(p => {
    data[p.id] = [];
    const count = p.id === 'life' ? 0 : Math.floor(Math.random() * 20) + 5; 
    for(let i=1; i<=count; i++) {
      data[p.id].push({
        id: `${p.id}-${i}`,
        title: `${p.name} - 极简主义测试文章 ${i}`,
        excerpt: `这是一篇关于${p.name}的测试文章内容预览，强调了现代化的设计语言与交互细节...`,
        date: `2026-06-${Math.floor(Math.random() * 30 + 1).toString().padStart(2, '0')}`
      });
    }
  });
  return data;
};

export const mockBlogData = generateMockData();
