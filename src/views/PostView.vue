<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import api from '../api';
import { showToast } from '../utils/toast';
import Compressor from 'compressorjs';

const router = useRouter();
const route = useRoute();

const title = ref('');
const content = ref('');
const showPreview = ref(false);

// Configure marked to handle oss_key prefix images
const renderer = new marked.Renderer();
const originalImage = renderer.image.bind(renderer);
renderer.image = (href, title, text) => {
  if (href.startsWith('oss_key:')) {
    const key = href.replace('oss_key:', '');
    const token = localStorage.getItem('access_token');
    if (token) {
      // Due to async nature of getImageUrl, we can't await it inside marked parser directly easily without complex async parsing.
      // So we render a proxy image URL that our backend proxy will handle for BOTH logged and unlogged users.
      // But for logged-in users, we might want signed URLs.
      // Easiest approach for marked synchronous parsing: just use the proxy GET endpoint.
      // Since unlogged users get 300px thumbnail and logged users might want full size, we can pass a token in query if we want full size via proxy,
      // or we just use proxy for everything in preview.
      return `<img src="${api.defaults.baseURL}/image/get_image?key=${encodeURIComponent(key)}" alt="${text || 'image'}">`;
    } else {
      return `<img src="${api.defaults.baseURL}/image/get_image?key=${encodeURIComponent(key)}" alt="${text || 'image'}">`;
    }
  }
  return originalImage(href, title, text);
};
marked.use({ renderer });

const renderedContent = computed(() => {
  // Convert markdown to HTML
  const rawHtml = marked.parse(content.value);
  // Sanitize the HTML
  return DOMPurify.sanitize(rawHtml);
});

const handleDraft = () => {
  showToast('草稿箱功能暂未实现', 'info');
};

const handleInsertImage = () => {
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = 'image/*';
  fileInput.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      showToast('准备上传图片...', 'info');

      // Compress if larger than 2MB
      let fileToUpload = file;
      if (file.size > 2 * 1024 * 1024) {
        const targetSize = 1.8 * 1024 * 1024;
        let estimatedQuality = targetSize / file.size;
        // 保证尽可能清晰，但也要压缩到1.8M左右
        estimatedQuality = Math.max(0.1, Math.min(estimatedQuality, 0.95));

        fileToUpload = await new Promise((resolve, reject) => {
          new Compressor(file, {
            quality: estimatedQuality,
            maxWidth: 1920,
            success: resolve,
            error: reject,
          });
        });
      }

      // 1. Get OSS Token
      const token = localStorage.getItem('access_token');
      let userId = 0;
      let email = "";
      if (token) {
         try {
            userId = parseInt(localStorage.getItem('user_id') || "0");
            email = localStorage.getItem('user_email') || "";
         } catch(e){}
      }

      // 确定文件扩展名，防止Blob对象没有name属性而默认变成webp
      let fileExt = 'jpeg';
      if (fileToUpload.name) {
        fileExt = fileToUpload.name.split('.').pop();
      } else if (file.name) {
        fileExt = file.name.split('.').pop();
      }
      if (fileToUpload.type) {
        const typeExt = fileToUpload.type.split('/').pop();
        if (typeExt && typeExt !== 'octet-stream') {
          fileExt = typeExt;
        }
      }

      const res = await api.post('/image/get_oss_upload_token', {
        base: { access_token: token, user_id: userId, email: email },
        file_ext: fileExt
      });

      if (res.data.errCode !== 0) {
        throw new Error(res.data.errMsg || '获取上传签名失败');
      }

      const uploadData = res.data.data || res.data;

      // 2. Upload to OSS using FormData
      const formData = new FormData();
      formData.append('key', uploadData.key);
      formData.append('policy', uploadData.policy);
      formData.append('OSSAccessKeyId', uploadData.oss_access_key_id);
      formData.append('signature', uploadData.signature);
      formData.append('success_action_status', '200');
      formData.append('file', fileToUpload);

      const uploadRes = await fetch(uploadData.host, {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) {
        throw new Error(`上传到OSS失败: ${uploadRes.status}`);
      }

      // 3. Insert Markdown into editor
      const imgMarkdown = `\n![图片](oss_key:${uploadData.key})\n`;
      content.value += imgMarkdown;
      showToast('图片上传成功！', 'success');

    } catch (err) {
      console.error(err);
      showToast(err.message || '图片上传失败', 'error');
    }
  };
  fileInput.click();
};

const openPreview = () => {
  showPreview.value = true;
};

const closePreview = () => {
  showPreview.value = false;
};

const publishPost = async () => {
  if (!title.value.trim()) {
    showToast('标题不能为空', 'error');
    return;
  }
  if (!content.value.trim()) {
    showToast('内容不能为空', 'error');
    return;
  }

  try {
    let authorIdStr = "0";
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const base64Url = token.split('.')[1];
        let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        while (base64.length % 4 !== 0) {
          base64 += '=';
        }
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        const match = jsonPayload.match(/"user_id":\s*(\d+)/);
        if (match) {
          authorIdStr = match[1];
        }
      } catch (e) {
        console.error('Failed to parse JWT for user_id', e);
      }
    }

    const targetPartition = route.query.partition || 'forum';
    const isAdminPost = targetPartition !== 'forum';

    // Build JSON payload manually to prevent Javascript Number precision loss for int64
    let payloadStr = '';
    let apiEndpoint = '';

    if (isAdminPost) {
      apiEndpoint = '/admin/push_blog_new';
      payloadStr = `{"title":${JSON.stringify(title.value)},"content":${JSON.stringify(content.value)},"category_id":${JSON.stringify(targetPartition)}}`;
    } else {
      apiEndpoint = '/bmanager/push_forum_new';
      payloadStr = `{"title":${JSON.stringify(title.value)},"content":${JSON.stringify(content.value)},"author_id":${authorIdStr}}`;
    }

    const res = await api.post(apiEndpoint, payloadStr, {
      headers: { 'Content-Type': 'application/json' }
    });

    if (res.data.errCode === 0) {
      showToast('发布成功！', 'success');
      router.push(`/${targetPartition}`); // Redirect back to target partition
    } else {
      showToast(res.data.errMsg || '发布失败', 'error');
    }
  } catch (err) {
    console.error('Publish error:', err);
    showToast('网络错误，发布失败', 'error');
  }
};
</script>

<template>
  <div class="post-view">
    <div class="editor-container">
      <input 
        v-model="title" 
        type="text" 
        class="title-input" 
        placeholder="请输入帖子标题..." 
      />
      
      <textarea 
        v-model="content" 
        class="content-textarea" 
        placeholder="在此输入帖子正文 (支持 Markdown)。如果你不懂 Markdown，只需输入普通文本即可，同样会有美观的渲染效果。"
      ></textarea>

      <div class="action-bar">
        <div class="left-actions">
          <button class="btn btn-secondary" @click="handleDraft">草稿箱</button>
          <button class="btn btn-secondary" @click="handleInsertImage">插入图片</button>
        </div>
        <div class="right-actions">
          <button class="btn btn-primary outline" @click="openPreview">预览</button>
          <button class="btn btn-primary" @click="publishPost">发布</button>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div v-if="showPreview" class="preview-modal-overlay" @click.self="closePreview">
      <div class="preview-modal">
        <button class="close-btn" @click="closePreview">×</button>
        <h1 class="preview-title">{{ title || '未命名标题' }}</h1>
        <div class="preview-content markdown-body" v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-view {
  width: 100%;
  height: calc(100vh - 40px); /* Account for padding */
  display: flex;
  flex-direction: column;
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 30px;
}

.title-input {
  font-size: 24px;
  font-weight: 700;
  border: none;
  background: transparent;
  color: var(--text-color);
  padding: 10px 0;
  border-bottom: 2px solid var(--border-color);
  outline: none;
  transition: border-color 0.2s;
}

.title-input:focus {
  border-bottom-color: var(--text-color);
}

.content-textarea {
  flex: 1;
  resize: none;
  border: none;
  background: transparent;
  color: var(--text-color);
  font-size: 16px;
  line-height: 1.6;
  padding: 10px 0;
  outline: none;
  font-family: inherit;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.left-actions, .right-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
}

.btn-secondary:hover {
  background: var(--text-color);
  color: var(--bg-color);
}

.btn-primary {
  background: var(--text-color);
  color: var(--bg-color);
  border: 1px solid var(--text-color);
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-primary.outline {
  background: transparent;
  color: var(--text-color);
}

.btn-primary.outline:hover {
  background: var(--text-color);
  color: var(--bg-color);
}

/* Preview Modal */
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
  width: 80%;
  max-width: 800px;
  height: 80vh;
  border-radius: 12px;
  padding: 40px;
  position: relative;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
}

.dark .preview-modal {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  font-size: 28px;
  line-height: 1;
  color: var(--text-color);
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

.preview-title {
  margin-top: 0;
  margin-bottom: 30px;
  font-size: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

/* Minimalist Markdown Rendering */
.markdown-body {
  font-family: inherit;
  line-height: 1.8;
  font-size: 16px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body :deep(p) {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(blockquote) {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin: 0 0 16px 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body :deep(img) {
  max-width: 100%;
  box-sizing: content-box;
  background-color: #fff;
}

.markdown-body :deep(pre) {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: var(--border-color);
  border-radius: 6px;
  margin-bottom: 16px;
}

.markdown-body :deep(code) {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: var(--border-color);
  border-radius: 3px;
  font-family: monospace;
}

.markdown-body :deep(pre code) {
  padding: 0;
  margin: 0;
  font-size: 100%;
  background: transparent;
}
</style>
