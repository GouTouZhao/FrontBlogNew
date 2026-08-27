import os

html_block = """
    <div class="content-wrapper" v-show="activeTab === 'generate'">
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
    <div class="card settings-card" v-show="activeTab === 'generate'">
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

    <div class="action-card" v-show="activeTab === 'generate'">
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
"""

with open(r'c:\Users\Lenovo\Desktop\MyBlogNew\front\src\views\ExamGeneratorView.vue', 'r', encoding='utf-8') as f:
    code = f.read()

target = '''          </button>
          <a :href="generateResult.pdf_url" target="_blank" class="download-btn" v-if="generateResult.pdf_url">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'''

code = code.replace(target, html_block + target)

with open(r'c:\Users\Lenovo\Desktop\MyBlogNew\front\src\views\ExamGeneratorView.vue', 'w', encoding='utf-8') as f:
    f.write(code)

print("Restored successfully.")
