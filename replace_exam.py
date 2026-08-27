import re

with open('src/views/ExamGeneratorView.vue', 'r', encoding='utf-8') as f:
    code = f.read()

new_script = """<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { showToast } from '../utils/toast';

const router = useRouter();

const goBack = () => {
  router.push('/apps');
};

// State
const colleges = ref([]);
const selectedCollegeId = ref('');
const courses = ref([]);
const selectedCourseId = ref('');

const showApplyCourseModal = ref(false);
const applyCourseForm = ref({
  course_name: '',
  course_category: '专业必修'
});

const keyPointFiles = ref([]);
const keyPointFileKeys = ref([]);
const isUploadingKeyPoint = ref(false);
const uploadProgressKeyPoint = ref(0);

const contentFiles = ref([]);
const contentFileKeys = ref([]);
const isUploadingContent = ref(false);
const uploadProgressContent = ref(0);

const isGenerating = ref(false);
const generateResult = ref(null);

const allowedExts = ['jpg', 'jpeg', 'png', 'pdf', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx'];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

// Initialize
onMounted(async () => {
  await fetchColleges();
});

const fetchColleges = async () => {
  try {
    const res = await api.post('/review/get_college_list', {
      page: 1,
      page_size: 100
    });
    if (res.data && res.data.errCode === 0) {
      colleges.value = res.data.data.list || [];
    } else {
      showToast(res.data?.errMsg || '获取学院列表失败', 'error');
    }
  } catch (err) {
    showToast('网络异常，获取学院列表失败', 'error');
  }
};

const handleCollegeChange = async () => {
  selectedCourseId.value = '';
  courses.value = [];
  if (!selectedCollegeId.value) return;

  try {
    const res = await api.post('/review/get_course_list', {
      college_id: Number(selectedCollegeId.value),
      status: 1, // 只获取正常课程
      page: 1,
      page_size: 100
    });
    if (res.data && res.data.errCode === 0) {
      courses.value = res.data.data.list || [];
    } else {
      showToast(res.data?.errMsg || '获取课程列表失败', 'error');
    }
  } catch (err) {
    showToast('网络异常，获取课程列表失败', 'error');
  }
};

const applyNewCourse = async () => {
  if (!selectedCollegeId.value) {
    showToast('请先选择学院', 'warning');
    return;
  }
  if (!applyCourseForm.value.course_name.trim()) {
    showToast('请输入课程名称', 'warning');
    return;
  }
  
  try {
    const res = await api.post('/review/apply_course', {
      college_id: Number(selectedCollegeId.value),
      course_name: applyCourseForm.value.course_name,
      course_category: applyCourseForm.value.course_category
    });
    if (res.data && res.data.errCode === 0) {
      showToast('申请成功，请等待管理员审核！', 'success');
      showApplyCourseModal.value = false;
      applyCourseForm.value.course_name = '';
    } else {
      showToast(res.data?.errMsg || '申请失败', 'error');
    }
  } catch (err) {
    showToast('网络异常，申请失败', 'error');
  }
};

// File handling
const handleFileChange = async (e, type) => {
  if (!selectedCollegeId.value || !selectedCourseId.value) {
    showToast('请先选择学院和课程！', 'warning');
    e.target.value = '';
    return;
  }

  const selectedFiles = Array.from(e.target.files);
  if (selectedFiles.length === 0) return;

  const file = selectedFiles[0]; 

  if (file.size > MAX_FILE_SIZE) {
    showToast(`文件大小不能超过 50MB: ${file.name}`, 'error');
    return;
  }

  // Validate extension
  const extMatch = file.name.match(/\.([^.]+)$/);
  const ext = extMatch ? extMatch[1].toLowerCase() : '';
  if (!allowedExts.includes(ext)) {
    showToast(`不支持的文件类型: ${ext}。支持: ${allowedExts.join(', ')}`, 'error');
    return;
  }

  const filesRef = type === 'keyPoint' ? keyPointFiles : contentFiles;
  const isUploadingRef = type === 'keyPoint' ? isUploadingKeyPoint : isUploadingContent;
  const progressRef = type === 'keyPoint' ? uploadProgressKeyPoint : uploadProgressContent;
  const fileKeysRef = type === 'keyPoint' ? keyPointFileKeys : contentFileKeys;

  filesRef.value.push({
    name: file.name,
    size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
    status: 'uploading'
  });
  
  const currentFileIndex = filesRef.value.length - 1;

  try {
    isUploadingRef.value = true;
    progressRef.value = 10;

    const sigRes = await api.post('/review/get_review_oss_key', {
      file_ext: ext
    });

    if (!sigRes.data || sigRes.data.errCode !== 0) {
      throw new Error(sigRes.data?.errMsg || '获取上传签名失败');
    }

    const ossData = sigRes.data.data;
    progressRef.value = 30;

    const formData = new FormData();
    formData.append('key', ossData.key);
    formData.append('policy', ossData.policy);
    formData.append('OSSAccessKeyId', ossData.oss_access_key_id);
    formData.append('success_action_status', '200');
    formData.append('signature', ossData.signature);
    formData.append('x-oss-security-token', ossData.security_token);
    formData.append('file', file);

    const uploadRes = await fetch(ossData.host, {
      method: 'POST',
      body: formData
    });

    if (!uploadRes.ok) {
      throw new Error(`上传失败: ${uploadRes.statusText}`);
    }

    progressRef.value = 100;
    
    fileKeysRef.value.push(ossData.key);
    filesRef.value[currentFileIndex].status = 'success';
    showToast('文件上传成功', 'success');

  } catch (err) {
    filesRef.value[currentFileIndex].status = 'error';
    showToast(err.message || '上传异常', 'error');
  } finally {
    isUploadingRef.value = false;
    setTimeout(() => { progressRef.value = 0; }, 1000);
    e.target.value = '';
  }
};

const generateExam = async () => {
  if (!selectedCourseId.value) {
    showToast('请选择课程', 'warning');
    return;
  }
  if (keyPointFileKeys.value.length === 0 && contentFileKeys.value.length === 0) {
    showToast('请先上传至少一个重点或内容文件', 'warning');
    return;
  }

  isGenerating.value = true;
  generateResult.value = null;

  try {
    const res = await api.post('/review/post_review_generate', {
      key_point_file_keys: keyPointFileKeys.value,
      content_file_keys: contentFileKeys.value,
      course_id: Number(selectedCourseId.value)
    });

    if (res.data && res.data.errCode === 0) {
      generateResult.value = res.data.data;
      showToast('任务提交成功！', 'success');
    } else {
      throw new Error(res.data?.errMsg || '生成请求失败');
    }
  } catch (err) {
    showToast(err.message || '网络异常', 'error');
  } finally {
    isGenerating.value = false;
  }
};

</script>"""

new_template = """<template>
  <div class="exam-generator-container">
    <div class="header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        返回应用中心
      </button>
      <h1 class="title">生成试卷助手</h1>
    </div>

    <!-- College and Course Selection -->
    <div class="selection-card card">
      <div class="selection-form">
        <div class="form-group selection-group">
          <label class="form-label">选择学院 (必选)</label>
          <select v-model="selectedCollegeId" class="select-input" @change="handleCollegeChange">
            <option value="" disabled>请选择学院</option>
            <option v-for="c in colleges" :key="c.college_id" :value="c.college_id">{{ c.college_name }}</option>
          </select>
        </div>

        <div class="form-group selection-group">
          <label class="form-label">选择课程 (必选)</label>
          <div class="course-select-row">
            <select v-model="selectedCourseId" class="select-input" :disabled="!selectedCollegeId">
              <option value="" disabled>请选择课程</option>
              <option v-for="c in courses" :key="c.course_id" :value="c.course_id">{{ c.course_name }}</option>
            </select>
            <button class="apply-btn" :disabled="!selectedCollegeId" @click="showApplyCourseModal = true">
              没找到？申请新增课程
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="left-panel">
        <div class="card" :class="{ 'disabled-card': !selectedCourseId }">
          <h2 class="card-title">1. 上传重点资料 (Key Points)</h2>
          <p class="card-desc">支持格式: jpg, pdf, ppt, doc, xls 等 (单文件上限50MB)</p>
          
          <div class="upload-area" :class="{ 'uploading': isUploadingKeyPoint, 'disabled-area': !selectedCourseId }">
            <input type="file" class="file-input" @change="e => handleFileChange(e, 'keyPoint')" :disabled="isUploadingKeyPoint || !selectedCourseId" accept=".jpg,.jpeg,.png,.pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx">
            <div class="upload-content">
              <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="upload-icon">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              <p v-if="!isUploadingKeyPoint">点击或拖拽文件到此处上传</p>
              <div v-else class="progress-bar-container">
                <div class="progress-bar" :style="{ width: uploadProgressKeyPoint + '%' }"></div>
                <p>上传中... {{ uploadProgressKeyPoint }}%</p>
              </div>
            </div>
          </div>

          <div class="file-list" v-if="keyPointFiles.length > 0">
            <div v-for="(file, index) in keyPointFiles" :key="index" class="file-item">
              <div class="file-info">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ file.size }}</span>
              </div>
              <div class="file-status" :class="file.status">
                <span v-if="file.status === 'uploading'">上传中...</span>
                <span v-else-if="file.status === 'success'">✅ 成功</span>
                <span v-else>❌ 失败</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="card" :class="{ 'disabled-card': !selectedCourseId }">
          <h2 class="card-title">2. 上传内容资料 (Contents)</h2>
          <p class="card-desc">上传需要全面覆盖的具体内容范围文件</p>
          
          <div class="upload-area" :class="{ 'uploading': isUploadingContent, 'disabled-area': !selectedCourseId }">
            <input type="file" class="file-input" @change="e => handleFileChange(e, 'content')" :disabled="isUploadingContent || !selectedCourseId" accept=".jpg,.jpeg,.png,.pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx">
            <div class="upload-content">
              <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="upload-icon">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              <p v-if="!isUploadingContent">点击或拖拽文件到此处上传</p>
              <div v-else class="progress-bar-container">
                <div class="progress-bar" :style="{ width: uploadProgressContent + '%' }"></div>
                <p>上传中... {{ uploadProgressContent }}%</p>
              </div>
            </div>
          </div>

          <div class="file-list" v-if="contentFiles.length > 0">
            <div v-for="(file, index) in contentFiles" :key="index" class="file-item">
              <div class="file-info">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ file.size }}</span>
              </div>
              <div class="file-status" :class="file.status">
                <span v-if="file.status === 'uploading'">上传中...</span>
                <span v-else-if="file.status === 'success'">✅ 成功</span>
                <span v-else>❌ 失败</span>
              </div>
            </div>
          </div>
        </div>

        <div class="action-card">
          <button 
            class="generate-btn" 
            :disabled="!selectedCourseId || (keyPointFileKeys.length === 0 && contentFileKeys.length === 0) || isGenerating"
            @click="generateExam"
          >
            <span v-if="isGenerating">提交生成中...</span>
            <span v-else>开始生成试卷</span>
          </button>

          <div v-if="generateResult" class="result-box">
            <div class="result-header">任务提交成功</div>
            <div class="result-item"><strong>Task ID:</strong> {{ generateResult.task_id }}</div>
            <div class="result-item"><strong>Status:</strong> {{ generateResult.status }}</div>
            <p class="result-hint">试卷生成由于需要使用大模型，可能需要几分钟时间，请稍后在后台查看生成结果。</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Apply Course Modal -->
    <div v-if="showApplyCourseModal" class="modal-overlay" @click.self="showApplyCourseModal = false">
      <div class="modal-content">
        <h3 class="modal-title">申请新增课程</h3>
        
        <div class="form-group">
          <label class="form-label">课程名称</label>
          <input v-model="applyCourseForm.course_name" type="text" class="text-input" placeholder="请输入课程完整名称">
        </div>

        <div class="form-group">
          <label class="form-label">课程类别</label>
          <select v-model="applyCourseForm.course_category" class="select-input">
            <option value="专业必修">专业必修</option>
            <option value="专业选修">专业选修</option>
            <option value="公共必修">公共必修</option>
            <option value="公共选修">公共选修</option>
          </select>
        </div>

        <div class="modal-actions">
          <button class="cancel-btn" @click="showApplyCourseModal = false">取消</button>
          <button class="confirm-btn" @click="applyNewCourse">提交申请</button>
        </div>
      </div>
    </div>

  </div>
</template>"""

code = re.sub(r'<script setup>[\s\S]*?</script>', new_script, code)
code = re.sub(r'<template>[\s\S]*?</template>', new_template, code)

styles_to_add = """
.selection-card {
  margin-bottom: 24px;
}

.selection-form {
  display: flex;
  gap: 24px;
}

.selection-group {
  flex: 1;
}

.select-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-color);
  color: var(--text-color);
  font-size: 14px;
  box-sizing: border-box;
}

.select-input:focus {
  outline: none;
  border-color: var(--text-color);
}

.select-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.course-select-row {
  display: flex;
  gap: 12px;
}

.apply-btn {
  padding: 0 16px;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  white-space: nowrap;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.apply-btn:hover:not(:disabled) {
  background: #3b82f6;
  color: white;
}

.apply-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.disabled-card {
  opacity: 0.6;
  pointer-events: none;
}

.disabled-area {
  cursor: not-allowed !important;
  opacity: 0.5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--text-color);
}

.text-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: transparent;
  color: var(--text-color);
  font-size: 14px;
  box-sizing: border-box;
}

.text-input:focus {
  outline: none;
  border-color: var(--text-color);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.cancel-btn {
  background: transparent;
  color: var(--text-color);
  opacity: 0.7;
}

.cancel-btn:hover {
  opacity: 1;
}

.confirm-btn {
  background: var(--text-color);
  color: var(--bg-color);
}

.confirm-btn:hover {
  opacity: 0.9;
}
"""

code = code.replace('</style>', styles_to_add + '\\n</style>')

with open('src/views/ExamGeneratorView.vue', 'w', encoding='utf-8') as f:
    f.write(code)
print("Done")
