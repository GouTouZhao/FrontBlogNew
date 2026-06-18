<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';
import { showToast } from '../utils/toast';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const route = useRoute();
const router = useRouter();

const article = ref(null);
const author = ref(null);
const isLoading = ref(true);

const commentContent = ref('');
const isSubmittingComment = ref(false);
const currentUser = ref(null);

const comments = ref([]);
const commentPage = ref(1);
const commentPageSize = 10;
const hasMoreComments = ref(true);
const isFetchingComments = ref(false);
const orderByLatest = ref(true);

const checkAuth = () => {
  const token = localStorage.getItem('access_token');
  const userId = localStorage.getItem('user_id');
  const nickname = localStorage.getItem('user_nickname');
  const email = localStorage.getItem('user_email');
  if (token && userId) {
    currentUser.value = { id: userId, email: email || '', token: token, nickname: nickname || '用户' };
  }
};

const fetchArticleDetails = async () => {
  try {
    const articleId = route.params.id;
    const res = await api.post('/static/get_article_details', { article_id: articleId });
    if (res.data) {
      const payload = res.data.data || res.data;
      article.value = payload.article || {};
      author.value = payload.user_info || null;
      
      viewTimer = setTimeout(async () => {
        try {
          await api.post('/static/add_view_count', { article_id: articleId });
          if (article.value) {
            article.value.view_count = (article.value.view_count || 0) + 1;
          }
        } catch (e) {
          console.error('Failed to add view count', e);
        }
      }, 30000);
    }
  } catch (error) {
    showToast('获取文章详情失败', 'error');
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

const fetchComments = async (reset = false) => {
  if (reset) {
    commentPage.value = 1;
    comments.value = [];
    hasMoreComments.value = true;
  }
  if (!hasMoreComments.value || isFetchingComments.value) return;

  isFetchingComments.value = true;
  try {
    const articleId = route.params.id;
    const res = await api.post('/static/get_comment_list', {
      article_id: articleId,
      page: commentPage.value,
      page_size: commentPageSize,
      order_by_latest: orderByLatest.value
    });
    
    if (res.data && (res.data.data || res.data.list)) {
      const payload = res.data.data || res.data;
      const list = payload.list || [];
      const total = payload.total_count || 0;
      
      list.forEach(c => {
        c.replying = false;
        c.replyContent = '';
        c.sonList = [];
        c.showSons = false;
        c.fetchingSons = false;
      });

      comments.value = [...comments.value, ...list];
      if (comments.value.length >= total) {
        hasMoreComments.value = false;
      } else {
        commentPage.value++;
      }
    }
  } catch (error) {
    console.error('获取评论失败', error);
  } finally {
    isFetchingComments.value = false;
  }
};

const toggleCommentOrder = () => {
  orderByLatest.value = !orderByLatest.value;
  fetchComments(true);
};

const handleScroll = () => {
  const bottomOfWindow = document.documentElement.scrollTop + window.innerHeight >= document.documentElement.offsetHeight - 100;
  if (bottomOfWindow) {
    fetchComments();
  }
};

const renderer = new marked.Renderer();
const originalImage = renderer.image.bind(renderer);
renderer.image = (href, title, text) => {
  if (href.startsWith('oss_key:')) {
    const key = href.replace('oss_key:', '');
    return `<img src="${api.defaults.baseURL}/image/get_image?key=${encodeURIComponent(key)}" alt="${text || 'image'}">`;
  }
  return originalImage(href, title, text);
};
marked.use({ renderer });

const deleteForum = async () => {
  if (!confirm('确定要删除这篇帖子吗？该操作不可恢复！')) return;
  try {
    const res = await api.post('/bmanager/delete_forum', {
      article_id: article.value.article_id,
      user_id: parseInt(currentUser.value.id)
    }, {
      headers: {
        'x-token': currentUser.value.token
      }
    });
    if (res.data && res.data.errCode === 0) {
      showToast('删除成功', 'success');
      router.push('/forum');
    } else {
      showToast(res.data.errMsg || '删除失败', 'error');
    }
  } catch (error) {
    console.error(error);
    showToast('删除失败', 'error');
  }
};

// Edit Post Modal
const isEditing = ref(false);
const editTitle = ref('');
const editContent = ref('');
const editCover = ref('');

const openEditModal = () => {
  editTitle.value = article.value.title;
  editContent.value = article.value.content;
  editCover.value = article.value.cover_image;
  isEditing.value = true;
};

const saveEdit = async () => {
  if (!editTitle.value.trim() || !editContent.value.trim()) {
    showToast('标题和内容不能为空', 'warning');
    return;
  }
  try {
    const payload = `{"article_id":${JSON.stringify(article.value.article_id)},"title":${JSON.stringify(editTitle.value)},"content":${JSON.stringify(editContent.value)},"cover_image":${JSON.stringify(editCover.value)},"user_id":${currentUser.value.id}}`;
    const res = await api.post('/bmanager/update_forum', payload, {
      headers: { 'Content-Type': 'application/json', 'x-token': currentUser.value.token }
    });
    if (res.data && res.data.errCode === 0) {
      showToast('修改成功', 'success');
      isEditing.value = false;
      fetchArticleDetails(); // reload details
    } else {
      showToast(res.data.errMsg || '修改失败', 'error');
    }
  } catch (error) {
    console.error(error);
    showToast('修改出错', 'error');
  }
};


const submitComment = async (replyToComment = null) => {
  let content = commentContent.value;
  let isReply = false;
  let rootId = 0;
  let replyToUserId = 0;

  if (replyToComment) {
    content = replyToComment.replyContent;
    if (!content.trim()) {
      showToast('回复内容不能为空', 'warning');
      return;
    }
    isReply = true;
    rootId = parseInt(replyToComment.id);
    replyToUserId = parseInt(replyToComment.user_info.user_id);
  } else {
    if (!content.trim()) {
      showToast('评论内容不能为空', 'warning');
      return;
    }
  }

  if (!currentUser.value) {
    showToast('请先登录后再操作', 'warning');
    return;
  }

  const submittingRef = replyToComment ? replyToComment : { submitting: false };
  submittingRef.submitting = true;
  if (!replyToComment) isSubmittingComment.value = true;

  try {
    const articleId = route.params.id;
    await api.post('/bmanager/push_forum_comment_new', {
      base: {
        access_token: currentUser.value.token,
        email: currentUser.value.email,
        user_id: parseInt(currentUser.value.id)
      },
      article_id: articleId,
      content: content,
      is_reply: isReply,
      root_comment_id: rootId,
      reply_to_user_id: replyToUserId
    });
    showToast('发表成功', 'success');
    
    if (replyToComment) {
      replyToComment.replyContent = '';
      replyToComment.replying = false;
      // Refresh son comments
      fetchSonComments(replyToComment, true);
    } else {
      commentContent.value = '';
      fetchComments(true);
    }
  } catch (error) {
    showToast('发表失败', 'error');
    console.error(error);
  } finally {
    submittingRef.submitting = false;
    if (!replyToComment) isSubmittingComment.value = false;
  }
};

const deleteComment = async (commentId, parentComment = null) => {
  if (!confirm('确定删除该评论吗？')) return;
  try {
    const res = await api.post('/bmanager/delete_comment', {
      comment_id: parseInt(commentId),
      user_id: parseInt(currentUser.value.id)
    });
    if (res.data && res.data.errCode === 0) {
      showToast('评论已删除', 'success');
      if (parentComment) {
        fetchSonComments(parentComment, true);
      } else {
        fetchComments(true);
      }
    } else {
      showToast(res.data.errMsg || '删除失败', 'error');
    }
  } catch (error) {
    console.error(error);
    showToast('删除失败', 'error');
  }
};

const fetchSonComments = async (comment, reset = false) => {
  if (reset) {
    comment.sonList = [];
    comment.sonPage = 1;
    comment.hasMoreSons = true;
  }
  
  if (!comment.sonPage) {
    comment.sonPage = 1;
    comment.hasMoreSons = true;
  }

  if (!comment.hasMoreSons || comment.fetchingSons) return;

  comment.fetchingSons = true;
  comment.showSons = true;
  
  try {
    const res = await api.post('/static/get_comment_son_list', {
      root_comment_id: comment.id,
      page: comment.sonPage,
      page_size: 10,
      order_by_latest: false
    });

    if (res.data && (res.data.data || res.data.list)) {
      const payload = res.data.data || res.data;
      const list = payload.list || [];
      const total = payload.total_count || 0;
      
      comment.sonList = [...comment.sonList, ...list];
      if (comment.sonList.length >= total) {
        comment.hasMoreSons = false;
      } else {
        comment.sonPage++;
      }
    }
  } catch (error) {
    console.error('获取子评论失败', error);
  } finally {
    comment.fetchingSons = false;
  }
};

const renderedContent = (content) => {
  return DOMPurify.sanitize(marked.parse(content || '暂无内容'));
};

let viewTimer = null;

onMounted(() => {
  checkAuth();
  fetchArticleDetails();
  fetchComments();
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  if (viewTimer) clearTimeout(viewTimer);
  window.removeEventListener('scroll', handleScroll);
});
</script>

<template>
  <div class="article-view">
    <div v-if="isLoading" class="loading">加载中...</div>
    <div v-else-if="!article" class="error">文章不存在或已被删除</div>
    <div v-else class="article-content">
      <button class="back-btn" @click="router.back()">返回</button>
      
      <div class="article-header">
        <h1 class="title">{{ article.title }}</h1>
        <div class="meta">
          <span v-if="author" class="author">作者: {{ author.nick_name }}</span>
          <span class="views">浏览量: {{ article.view_count }}</span>
          <span class="time" v-if="article.updated_at">最后更新: {{ new Date(article.updated_at * 1000).toLocaleString() }}</span>
        </div>
      </div>

      <div v-if="article.cover_image" class="cover-image">
        <img :src="article.cover_image" alt="Cover" />
      </div>

      <div class="markdown-body" v-html="renderedContent(article.content)"></div>

      <div class="article-actions" v-if="currentUser && article.author_id === currentUser.id">
        <button class="edit-btn" @click="openEditModal">修改</button>
        <button class="delete-btn" @click="deleteForum">删除</button>
      </div>

      <div class="comments-section">
        <div class="comments-header">
          <h3>评论区</h3>
          <button class="order-toggle-btn" @click="toggleCommentOrder">
            切换顺序 (当前: {{ orderByLatest ? '最晚' : '最早' }})
          </button>
        </div>

        <div class="comment-input-area">
          <textarea 
            v-model="commentContent" 
            placeholder="写下你的评论..." 
            rows="4"
          ></textarea>
          <button 
            class="submit-comment-btn" 
            @click="submitComment(null)" 
            :disabled="isSubmittingComment"
          >
            {{ isSubmittingComment ? '提交中...' : '发表' }}
          </button>
        </div>

        <div class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item fade-in">
            <div class="comment-top">
              <span class="comment-author">{{ comment.user_info?.nick_name || '用户' }}</span>
              <span class="comment-time">{{ new Date(comment.created_at * 1000).toLocaleString() }}</span>
            </div>
            <div class="comment-text">{{ comment.content }}</div>
            
            <div class="comment-actions">
              <button class="action-btn" @click="comment.replying = !comment.replying">回复</button>
              <button class="action-btn" v-if="comment.has_children" @click="fetchSonComments(comment)">查看回复</button>
              <button class="action-btn delete" v-if="currentUser && comment.user_info?.user_id === currentUser.id" @click="deleteComment(comment.id)">删除</button>
            </div>

            <!-- Reply Input Box -->
            <div v-if="comment.replying" class="reply-input-area fade-in">
              <textarea v-model="comment.replyContent" placeholder="回复评论..." rows="2"></textarea>
              <div class="reply-actions">
                <button class="cancel-btn" @click="comment.replying = false">取消</button>
                <button class="submit-comment-btn" @click="submitComment(comment)" :disabled="comment.submitting">发送</button>
              </div>
            </div>

            <!-- Sub Comments -->
            <div v-if="comment.showSons" class="sub-comments">
              <div v-for="son in comment.sonList" :key="son.id" class="comment-item sub-comment fade-in">
                <div class="comment-top">
                  <span class="comment-author">{{ son.user_info?.nick_name || '用户' }} <span v-if="son.reply_to_user_info" class="reply-label">回复 {{ son.reply_to_user_info.nick_name }}</span></span>
                  <span class="comment-time">{{ new Date(son.created_at * 1000).toLocaleString() }}</span>
                </div>
                <div class="comment-text">{{ son.content }}</div>
                <div class="comment-actions">
                  <!-- Note: Subcomments can also be replied to, which effectively replies to the root thread -->
                  <button class="action-btn delete" v-if="currentUser && son.user_info?.user_id === currentUser.id" @click="deleteComment(son.id, comment)">删除</button>
                </div>
              </div>
              <button class="action-btn load-more" v-if="comment.hasMoreSons && !comment.fetchingSons" @click="fetchSonComments(comment)">加载更多回复</button>
              <div v-if="comment.fetchingSons" class="loading-small">加载中...</div>
            </div>

          </div>
          
          <div v-if="isFetchingComments" class="loading-more">正在加载评论...</div>
          <div v-else-if="!hasMoreComments && comments.length > 0" class="no-more">—— 我也是有底线的 ——</div>
          <div v-else-if="comments.length === 0" class="no-more">暂无评论，快来抢沙发吧</div>
        </div>

      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="isEditing" class="preview-modal-overlay" @click.self="isEditing = false">
      <div class="preview-modal">
        <button class="close-btn" @click="isEditing = false">×</button>
        <h2 style="margin-top:0;">修改帖子</h2>
        <input class="edit-input title-input" v-model="editTitle" placeholder="标题" />
        <input class="edit-input" v-model="editCover" placeholder="封面图片链接 (选填)" />
        <textarea class="edit-textarea" v-model="editContent" placeholder="帖子内容..."></textarea>
        <div class="edit-actions">
          <button class="cancel-btn" @click="isEditing = false">取消</button>
          <button class="submit-btn" @click="saveEdit">保存修改</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.article-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

.back-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 24px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--border-color);
}

.article-header {
  margin-bottom: 30px;
}

.title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 16px;
  line-height: 1.2;
}

.meta {
  display: flex;
  gap: 16px;
  font-size: 0.9rem;
  opacity: 0.7;
}

.cover-image {
  margin-bottom: 30px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.cover-image img {
  width: 100%;
  height: auto;
  display: block;
}

.markdown-body {
  font-size: 1.1rem;
  line-height: 1.8;
  margin-bottom: 30px;
}

.article-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 40px;
  padding-top: 20px;
  border-top: 1px dashed var(--border-color);
}

.edit-btn, .delete-btn {
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  border: none;
  font-weight: 600;
}

.edit-btn {
  background: var(--text-color);
  color: var(--bg-color);
}

.delete-btn {
  background: #ff4d4f;
  color: #fff;
}

.comments-section {
  border-top: 1px solid var(--border-color);
  padding-top: 30px;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.order-toggle-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 4px 12px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 0.85rem;
}

.comment-input-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
  margin-bottom: 30px;
}

textarea {
  width: 100%;
  background: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.2s;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: var(--text-color);
}

.submit-comment-btn {
  align-self: flex-end;
  background: var(--text-color);
  color: var(--bg-color);
  border: none;
  padding: 8px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.cancel-btn {
  background: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.submit-comment-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-comment-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  padding: 16px;
  background: rgba(128, 128, 128, 0.05);
  border-radius: 12px;
  border: 1px solid transparent;
}

.dark .comment-item {
  background: rgba(255, 255, 255, 0.05);
}

.comment-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.comment-author {
  font-weight: 600;
  color: var(--text-color);
}

.reply-label {
  font-weight: normal;
  opacity: 0.7;
  font-size: 0.8rem;
  margin-left: 8px;
}

.comment-time {
  opacity: 0.6;
}

.comment-text {
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 12px;
  white-space: pre-wrap;
}

.comment-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
}

.action-btn {
  background: transparent;
  border: none;
  color: var(--text-color);
  opacity: 0.6;
  cursor: pointer;
  font-size: 0.85rem;
}

.action-btn:hover {
  opacity: 1;
  text-decoration: underline;
}

.action-btn.delete {
  color: #ff4d4f;
}

.reply-input-area {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.sub-comments {
  margin-top: 16px;
  margin-left: 20px;
  padding-left: 16px;
  border-left: 2px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sub-comment {
  padding: 12px;
  background: transparent;
  border: 1px solid var(--border-color);
}

.load-more {
  text-align: left;
  margin-top: 8px;
}

.loading-more, .no-more, .loading-small {
  text-align: center;
  padding: 20px;
  opacity: 0.6;
  font-size: 0.9rem;
}

/* Edit Modal */
.preview-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.preview-modal {
  background: var(--bg-color);
  color: var(--text-color);
  width: 90%;
  max-width: 800px;
  height: auto;
  max-height: 90vh;
  border-radius: 12px;
  padding: 30px;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-color);
}

.edit-input {
  width: 100%;
  background: transparent;
  border: 1px solid var(--border-color);
  padding: 12px;
  border-radius: 8px;
  color: var(--text-color);
  font-size: 1rem;
}

.title-input {
  font-size: 1.2rem;
  font-weight: bold;
}

.edit-textarea {
  flex: 1;
  min-height: 300px;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.submit-btn {
  background: var(--text-color);
  color: var(--bg-color);
  border: none;
  padding: 8px 24px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
