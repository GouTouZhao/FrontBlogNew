import os
import re

with open('current_script.txt', 'r', encoding='utf-8') as f:
    script_content = f.read()

template_content = """<template>
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
              <input type="file" class="file-input" @click="handleInputClick" @change="e => handleFileChange(e, 'keyPoint')" :disabled="isUploadingKeyPoint" accept=".jpg,.jpeg,.png,.pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx">
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
              <input type="file" class="file-input" @click="handleInputClick" @change="e => handleFileChange(e, 'content')" :disabled="isUploadingContent" accept=".jpg,.jpeg,.png,.pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx">
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
              <input type="file" class="file-input" @click="handleInputClick" @change="e => handleFileChange(e, 'pastExam')" :disabled="isUploadingPastExam" accept=".jpg,.jpeg,.png,.pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx">
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
            <h3>任务 ID: {{ item.task_id }}</h3>
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
"""

with open('src/views/ExamGeneratorView.vue', 'r', encoding='utf-8') as f:
    full_code = f.read()

# Extract styles
style_content = re.search(r'<style scoped>.*?</style>', full_code, re.S)
if style_content:
    style_content = style_content.group(0)
else:
    # If not found, use a fallback from a previous step, but it should exist.
    style_content = "<style scoped></style>"

final_code = script_content + "\\n\\n" + template_content + "\\n\\n" + style_content

with open('src/views/ExamGeneratorView.vue', 'w', encoding='utf-8') as f:
    f.write(final_code)
print("Finished rewriting cleanly.")
