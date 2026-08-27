<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { showToast } from '../utils/toast';

const router = useRouter();

const goBack = () => {
  router.push('/apps');
};

const getBase = () => ({
  access_token: localStorage.getItem('access_token') || '',
  email: localStorage.getItem('user_email') || '',
  user_id: Number(localStorage.getItem('user_id') || 0)
});

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

const pastExamFiles = ref([]);
const pastExamFileKeys = ref([]);
const isUploadingPastExam = ref(false);
const uploadProgressPastExam = ref(0);

const isGenerating = ref(false);
const generateResult = ref(null);
const parsedQuestions = computed(() => {
  if (!generateResult.value || !generateResult.value.content) return [];
  try {
    return JSON.parse(generateResult.value.content);
  } catch (e) {
    return [];
  }
});
const showResultModal = ref(false);

// Question counts
const singleChoiceCount = ref(8);
const multipleChoiceCount = ref(0);
const trueFalseCount = ref(0);
const fillInBlankCount = ref(0);
const shortAnswerCount = ref(0);
const generalPrompt = ref('');

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
      college_id: String(selectedCollegeId.value),
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
      base: getBase(),
      college_id: String(selectedCollegeId.value),
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
const handleInputClick = (e) => {
  if (!selectedCollegeId.value || !selectedCourseId.value) {
    e.preventDefault();
    showToast('请先选择上面的学院和课程！', 'warning');
  }
};

const handleFileChange = async (e, type) => {
  if (!selectedCollegeId.value || !selectedCourseId.value) {
    showToast('请先选择学院和课程！', 'warning');
    e.target.value = '';
    return;
  }

  const selectedFiles = Array.from(e.target.files);
  if (selectedFiles.length === 0) return;

  const filesRef = type === 'keyPoint' ? keyPointFiles : (type === 'content' ? contentFiles : pastExamFiles);
  const isUploadingRef = type === 'keyPoint' ? isUploadingKeyPoint : (type === 'content' ? isUploadingContent : isUploadingPastExam);
  const progressRef = type === 'keyPoint' ? uploadProgressKeyPoint : (type === 'content' ? uploadProgressContent : uploadProgressPastExam);
  const fileKeysRef = type === 'keyPoint' ? keyPointFileKeys : (type === 'content' ? contentFileKeys : pastExamFileKeys);

  isUploadingRef.value = true;
  let successCount = 0;

  for (let i = 0; i < selectedFiles.length; i++) {
    const file = selectedFiles[i];

    if (file.size > MAX_FILE_SIZE) {
      showToast(`文件大小不能超过 50MB: ${file.name}`, 'error');
      continue;
    }

    // Validate extension
    const extMatch = file.name.match(/\.([^.]+)$/);
    const ext = extMatch ? extMatch[1].toLowerCase() : '';
    if (!allowedExts.includes(ext)) {
      showToast(`不支持的文件类型: ${ext}。支持: ${allowedExts.join(', ')}`, 'error');
      continue;
    }

    filesRef.value.push({
      name: file.name,
      size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
      status: 'uploading'
    });
    
    const currentFileIndex = filesRef.value.length - 1;

    try {
      progressRef.value = Math.floor((i / selectedFiles.length) * 100) + 10;

      const sigRes = await api.post('/review/get_review_oss_key', {
        base: getBase(),
        file_ext: ext
      });

      if (!sigRes.data || sigRes.data.errCode !== 0) {
        throw new Error(sigRes.data?.errMsg || '获取上传签名失败');
      }

      const ossData = sigRes.data.data;
      progressRef.value = Math.floor((i / selectedFiles.length) * 100) + 30;

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

      fileKeysRef.value.push(ossData.key);
      filesRef.value[currentFileIndex].status = 'success';
      successCount++;

    } catch (err) {
      filesRef.value[currentFileIndex].status = 'error';
      showToast(`${file.name} 上传异常: ${err.message}`, 'error');
    }
  }

  progressRef.value = 100;
  isUploadingRef.value = false;
  setTimeout(() => { progressRef.value = 0; }, 1000);
  e.target.value = '';

  if (successCount > 0) {
    showToast(`成功上传 ${successCount} 个文件`, 'success');
  }
};

const generateExam = async () => {
  if (!selectedCourseId.value) {
    showToast('请选择课程', 'warning');
    return;
  }
  if (keyPointFileKeys.value.length === 0 && contentFileKeys.value.length === 0 && pastExamFileKeys.value.length === 0) {
    showToast('请先上传至少一个重点、内容或试卷文件', 'warning');
    return;
  }

  if (
    singleChoiceCount.value < 0 ||
    multipleChoiceCount.value < 0 ||
    trueFalseCount.value < 0 ||
    fillInBlankCount.value < 0 ||
    shortAnswerCount.value < 0
  ) {
    showToast('题型数量不能为负数', 'warning');
    return;
  }

  if (
    singleChoiceCount.value > 20 ||
    trueFalseCount.value > 20 ||
    fillInBlankCount.value > 20
  ) {
    showToast('单选、判断、填空最多为20道', 'warning');
    return;
  }

  if (
    multipleChoiceCount.value > 10 ||
    shortAnswerCount.value > 10
  ) {
    showToast('多选、简答最多为10道', 'warning');
    return;
  }
  
  const totalQuestions = 
    singleChoiceCount.value + 
    multipleChoiceCount.value + 
    trueFalseCount.value + 
    fillInBlankCount.value + 
    shortAnswerCount.value;

  if (totalQuestions <= 0) {
    showToast('总题数必须大于0', 'warning');
    return;
  }

  isGenerating.value = true;
  generateResult.value = null;

  try {
    const res = await api.post('/review/post_review_generate', {
      base: getBase(),
      key_point_file_keys: keyPointFileKeys.value,
      content_file_keys: contentFileKeys.value,
      past_exam_file_keys: pastExamFileKeys.value,
      course_id: String(selectedCourseId.value),
      single_choice_count: singleChoiceCount.value,
      multiple_choice_count: multipleChoiceCount.value,
      true_false_count: trueFalseCount.value,
      fill_in_blank_count: fillInBlankCount.value,
      short_answer_count: shortAnswerCount.value,
      general_prompt: generalPrompt.value
    }, {
      timeout: 600000 // 10 minutes timeout for long-running task
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

// History State
const activeTab = ref('generate'); // 'generate' or 'history'
const historyList = ref([]);
const isFetchingHistory = ref(false);

const fetchHistory = async () => {
  if (isFetchingHistory.value) return;
  isFetchingHistory.value = true;
  try {
    const res = await api.post('/review/get_user_exam_history', {
      base: getBase(),
      page: 1,
      page_size: 50
    });
    if (res.data && res.data.errCode === 0) {
      historyList.value = res.data.data.list || [];
    } else {
      showToast(res.data?.errMsg || '获取记录失败', 'error');
    }
  } catch (err) {
    showToast('网络异常，获取记录失败', 'error');
  } finally {
    isFetchingHistory.value = false;
  }
};

const switchTab = (tab) => {
  activeTab.value = tab;
  if (tab === 'history') {
    fetchHistory();
  }
};

const viewHistoryDetail = (item) => {
  generateResult.value = {
    content: item.result_content,
    pdfUrl: item.pdf_url,
    taskId: item.task_id
  };
  showResultModal.value = true;
};

</script>\n\n<template>
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

    <!-- Tabs -->
    <div class="tabs-container">
      <div class="tab" :class="{ active: activeTab === 'generate' }" @click="switchTab('generate')">生成试卷</div>
      <div class="tab" :class="{ active: activeTab === 'history' }" @click="switchTab('history')">生成记录</div>
    </div>

    <div v-show="activeTab === 'generate'">
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
        <div class="upload-panel">
          <div class="card" :class="{ 'disabled-card': !selectedCourseId }">
            <h2 class="card-title">1. 上传重点资料</h2>
            <p class="card-desc">支持格式: jpg, pdf, ppt, doc, xls 等 (单文件上限50MB)</p>
            
            <div class="upload-area" :class="{ 'uploading': isUploadingKeyPoint, 'disabled-area': !selectedCourseId }">
              <input type="file" multiple class="file-input" @click="handleInputClick" @change="e => handleFileChange(e, 'keyPoint')" :disabled="isUploadingKeyPoint" accept=".jpg,.jpeg,.png,.pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx">
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

        <div class="upload-panel">
          <div class="card" :class="{ 'disabled-card': !selectedCourseId }">
            <h2 class="card-title">2. 上传内容资料</h2>
            <p class="card-desc">上传需要全面覆盖的具体内容范围文件</p>
            
            <div class="upload-area" :class="{ 'uploading': isUploadingContent, 'disabled-area': !selectedCourseId }">
              <input type="file" multiple class="file-input" @click="handleInputClick" @change="e => handleFileChange(e, 'content')" :disabled="isUploadingContent" accept=".jpg,.jpeg,.png,.pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx">
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
        </div>

        <div class="upload-panel">
          <div class="card" :class="{ 'disabled-card': !selectedCourseId }">
            <h2 class="card-title">3. 上传真题试卷</h2>
            <p class="card-desc">上传历年真题或相关试卷用于参考题型</p>
            
            <div class="upload-area" :class="{ 'uploading': isUploadingPastExam, 'disabled-area': !selectedCourseId }">
              <input type="file" multiple class="file-input" @click="handleInputClick" @change="e => handleFileChange(e, 'pastExam')" :disabled="isUploadingPastExam" accept=".jpg,.jpeg,.png,.pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx">
              <div class="upload-content">
                <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="upload-icon">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p v-if="!isUploadingPastExam">点击或拖拽文件到此处上传</p>
                <div v-else class="progress-bar-container">
                  <div class="progress-bar" :style="{ width: uploadProgressPastExam + '%' }"></div>
                  <p>上传中... {{ uploadProgressPastExam }}%</p>
                </div>
              </div>
            </div>

            <div class="file-list" v-if="pastExamFiles.length > 0">
              <div v-for="(file, index) in pastExamFiles" :key="index" class="file-item">
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
      </div>

      <!-- Question Settings -->
      <div class="card settings-card">
        <h2 class="card-title">题型与数量设置</h2>
        <p class="card-desc">配置你需要生成的各类题目数量</p>
        
        <div class="settings-grid">
          <div class="form-group">
            <label class="form-label">单选题数量</label>
            <input type="number" min="0" max="20" v-model.number="singleChoiceCount" class="number-input">
          </div>
          <div class="form-group">
            <label class="form-label">多选题数量</label>
            <input type="number" min="0" max="10" v-model.number="multipleChoiceCount" class="number-input">
          </div>
          <div class="form-group">
            <label class="form-label">判断题数量</label>
            <input type="number" min="0" max="20" v-model.number="trueFalseCount" class="number-input">
          </div>
          <div class="form-group">
            <label class="form-label">填空题数量</label>
            <input type="number" min="0" max="20" v-model.number="fillInBlankCount" class="number-input">
          </div>
          <div class="form-group">
            <label class="form-label">简答题数量</label>
            <input type="number" min="0" max="10" v-model.number="shortAnswerCount" class="number-input">
          </div>
        </div>
        
        <div class="form-group" style="margin-top: 20px;">
          <label class="form-label">总提示词 (非必填)</label>
          <p class="form-hint">例如：请着重考察第三章的网络分层架构，题目难度尽量偏大</p>
          <textarea v-model="generalPrompt" class="tag-input" rows="3" placeholder="请输入你的补充要求..." style="resize: vertical;"></textarea>
        </div>
      </div>

      <div class="action-card">
        <button 
          class="generate-btn" 
          :disabled="!selectedCourseId || (keyPointFileKeys.length === 0 && contentFileKeys.length === 0 && pastExamFileKeys.length === 0) || isGenerating"
          @click="generateExam"
        >
          <span v-if="isGenerating">提交生成中...</span>
          <span v-else>开始生成试卷</span>
        </button>

        <div v-if="generateResult" class="result-box">
          <div class="result-header">🎉 试卷生成成功</div>
          <div class="result-item"><strong>Task ID:</strong> {{ generateResult.task_id }}</div>
          
          <div class="result-actions" v-if="generateResult.content">
            <button class="view-btn" @click="showResultModal = true">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
              查看排版试卷
            </button>
            <a :href="generateResult.pdf_url" target="_blank" class="download-btn" v-if="generateResult.pdf_url">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              下载 PDF
            </a>
          </div>
          <p class="result-hint" v-if="!generateResult.content">试卷生成由于需要使用大模型，可能需要几分钟时间，请稍后在后台查看生成结果。</p>
        </div>
      </div>
    </div> <!-- end of generate tab -->

    <!-- History Tab Content -->
    <div v-show="activeTab === 'history'" class="history-wrapper">
      <div v-if="isFetchingHistory" class="loading-state">
        <p>加载中...</p>
      </div>
      <div v-else-if="historyList.length === 0" class="empty-state">
        <p>暂无生成记录</p>
      </div>
      <div v-else class="history-list">
        <div v-for="item in historyList" :key="item.task_id" class="history-item card">
          <div class="history-item-header">
            <div>
              <h3>任务 ID: {{ item.task_id }}</h3>
              <div v-if="item.course_name" class="history-tags" style="margin-top: 6px;">
                <span style="font-size: 12px; background: #eef2ff; color: #4f46e5; padding: 2px 8px; border-radius: 4px; margin-right: 8px;">{{ item.college_name }}</span>
                <span style="font-size: 12px; background: #f0fdf4; color: #16a34a; padding: 2px 8px; border-radius: 4px;">{{ item.course_name }}</span>
              </div>
            </div>
            <span class="history-date">{{ item.created_at || '刚刚' }}</span>
          </div>
          <div class="history-item-body">
            <p><strong>题型组成:</strong> 单选({{item.single_choice_count || 0}}), 多选({{item.multiple_choice_count || 0}}), 判断({{item.true_false_count || 0}}), 填空({{item.fill_in_blank_count || 0}}), 简答({{item.short_answer_count || 0}})</p>
          </div>
          <div class="history-item-actions result-actions">
            <button class="view-btn" @click="viewHistoryDetail(item)" v-if="item.result_content">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
              查看排版试卷
            </button>
            <span v-else class="history-date" style="margin-right: 15px">生成中，请稍后...</span>
            <a :href="item.pdf_url" target="_blank" class="download-btn" v-if="item.pdf_url">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              下载 PDF
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Result Modal -->
    <div v-if="showResultModal" class="modal-overlay" @click.self="showResultModal = false">
      <div class="modal-content exam-modal-content">
        <div class="modal-header">
          <h3 class="modal-title">试卷内容预览</h3>
          <button class="close-btn" @click="showResultModal = false">&times;</button>
        </div>
        <div class="exam-preview">
          <div v-for="(q, index) in parsedQuestions" :key="index" class="question-item">
            <div class="q-title"><strong>{{ index + 1 }}. [{{ q.type }}]</strong> {{ q.question }}</div>
            <div class="q-options" v-if="(q.type === 'single_choice' || q.type === 'multiple_choice') && q.options">
              <div v-for="(optText, optKey) in q.options" :key="optKey" class="q-opt">
                {{ optKey }}. {{ optText }}
              </div>
            </div>
            <div class="q-answer"><strong>【参考答案】</strong> {{ q.answer }}</div>
            <div class="q-explanation"><strong>【解析】</strong> {{ q.explanation }}</div>
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
</template>
\n\n<style scoped>
.exam-generator-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.header {
  margin-bottom: 30px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--text-color);
  opacity: 0.7;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  padding: 0;
  width: fit-content;
}

.back-btn:hover {
  opacity: 1;
}

.title {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-color);
}

.content-wrapper {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.upload-panel {
  min-width: 0;
}

@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
}

.card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-color);
}

.card-desc {
  font-size: 13px;
  opacity: 0.6;
  margin-bottom: 20px;
  color: var(--text-color);
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  position: relative;
  transition: border-color 0.2s, background-color 0.2s;
  cursor: pointer;
}

.upload-area:hover {
  border-color: var(--text-color);
  background-color: rgba(128, 128, 128, 0.05);
}

.upload-area.uploading {
  cursor: not-allowed;
  opacity: 0.8;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.file-input:disabled {
  cursor: not-allowed;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-color);
  opacity: 0.7;
  position: relative;
  z-index: 1;
  pointer-events: none;
}

.upload-icon {
  margin-bottom: 8px;
}

.progress-bar-container {
  width: 100%;
  max-width: 300px;
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 10px;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: var(--text-color);
  transition: width 0.3s ease;
}

.file-list {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(128, 128, 128, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-color);
}

.file-size {
  font-size: 12px;
  opacity: 0.6;
  color: var(--text-color);
}

.file-status {
  font-size: 13px;
  font-weight: 600;
}

.file-status.success { color: #10b981; }
.file-status.error { color: #ef4444; }
.file-status.uploading { color: #3b82f6; opacity: 0.8; }

.form-group {
  margin-bottom: 24px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: var(--text-color);
}

.form-hint {
  font-size: 12px;
  opacity: 0.6;
  margin-bottom: 12px;
  color: var(--text-color);
}

.tag-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: transparent;
  color: var(--text-color);
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
  margin-bottom: 12px;
}

.tag-input:focus {
  outline: none;
  border-color: var(--text-color);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(128, 128, 128, 0.1);
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-color);
}

.tag-close {
  background: none;
  border: none;
  color: var(--text-color);
  opacity: 0.5;
  cursor: pointer;
  padding: 0;
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-close:hover {
  opacity: 1;
}

.action-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.generate-btn {
  width: 100%;
  padding: 16px;
  background: var(--text-color);
  color: var(--bg-color);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
}

.generate-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.generate-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.result-box {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 12px;
  padding: 20px;
  color: var(--text-color);
}

.result-header {
  font-weight: 700;
  font-size: 16px;
  margin-bottom: 12px;
  color: #10b981;
}

.result-item {
  font-size: 14px;
  margin-bottom: 6px;
}

.result-hint {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 12px;
  border-top: 1px solid rgba(128, 128, 128, 0.2);
  padding-top: 12px;
}

@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
  }
}

.selection-card {
  margin-bottom: 24px;
}

.settings-card {
  margin-bottom: 24px;
}

.settings-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.settings-grid .form-group {
  flex: 1;
  min-width: 120px;
  margin-bottom: 0;
}

.number-input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: transparent;
  color: var(--text-color);
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.number-input:focus {
  outline: none;
  border-color: var(--text-color);
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
  margin-top: 24px;
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border: none;
}

.cancel-btn {
  background: var(--border-color);
  color: var(--text-color);
}

.confirm-btn {
  background: var(--text-color);
  color: var(--bg-color);
}

.result-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.view-btn, .download-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: opacity 0.2s;
  border: none;
}

.view-btn {
  background: rgba(128, 128, 128, 0.1);
  color: var(--text-color);
}

.download-btn {
  background: #10b981;
  color: white;
}

.view-btn:hover, .confirm-btn:hover {
  opacity: 0.9;
}

/* Tabs */
.tabs-container {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}
.tab {
  padding: 12px 24px;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-color);
  opacity: 0.6;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.tab.active {
  opacity: 1;
  border-bottom-color: #3b82f6;
  color: #3b82f6;
}
.tab:hover {
  opacity: 1;
}

/* History */
.history-wrapper {
  margin-top: 24px;
}
.history-item {
  margin-bottom: 16px;
  padding: 20px;
}
.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.history-item-header h3 {
  margin: 0;
  font-size: 16px;
}
.history-date {
  font-size: 14px;
  color: var(--text-color);
  opacity: 0.6;
}
.history-item-body {
  margin-bottom: 16px;
  font-size: 14px;
  opacity: 0.8;
}
.history-item-actions {
  justify-content: flex-start;
}
.empty-state, .loading-state {
  text-align: center;
  padding: 40px;
  color: var(--text-color);
  opacity: 0.6;
}

.exam-modal-content {
  max-width: 800px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-color);
  cursor: pointer;
  opacity: 0.6;
}

.close-btn:hover {
  opacity: 1;
}

.exam-preview {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-item {
  background: rgba(128, 128, 128, 0.05);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.q-title {
  font-size: 15px;
  margin-bottom: 12px;
  line-height: 1.5;
}

.q-options {
  margin-bottom: 12px;
  padding-left: 16px;
}

.q-opt {
  font-size: 14px;
  margin-bottom: 6px;
}

.q-answer {
  color: #10b981;
  margin-bottom: 8px;
  font-size: 14px;
}

.q-explanation {
  font-size: 14px;
  opacity: 0.8;
  line-height: 1.5;
}
</style>