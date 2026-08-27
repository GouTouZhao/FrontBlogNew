<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { showToast } from '../utils/toast';

const router = useRouter();

const goBack = () => {
  router.push('/apps');
};

const isAdmin = computed(() => localStorage.getItem('user_email') === '2460607806@qq.com');

const getBase = () => ({
  access_token: localStorage.getItem('access_token') || '',
  email: localStorage.getItem('user_email') || '',
  user_id: Number(localStorage.getItem('user_id') || 0)
});

const activeTab = ref('pending'); // 'pending', 'colleges', 'courses'

const pendingCourses = ref([]);
const collegesList = ref([]);
const coursesList = ref([]);
const collegesMap = ref({});
const isLoading = ref(false);

const uploadTasks = ref([]);
const uploadFiles = ref([]);
const showFilesModal = ref(false);
const currentTaskId = ref(null);

// Modals
const showCollegeModal = ref(false);
const editingCollege = ref(null);
const collegeForm = ref({ college_name: '', college_code: '', description: '' });

const showCourseModal = ref(false);
const editingCourse = ref(null);
const courseForm = ref({ course_name: '', college_id: '', course_category: '' });

onMounted(async () => {
  if (!isAdmin.value) {
    showToast('无权限访问此页面', 'error');
    router.replace('/');
    return;
  }
  await fetchColleges();
  await fetchPendingCourses();
  await fetchAllCourses();
  await fetchUploadTasks();
});

const switchTab = (tab) => {
  activeTab.value = tab;
};

const fetchColleges = async () => {
  try {
    const res = await api.post('/review/get_college_list', {
      base: getBase(),
      page: 1,
      page_size: 1000
    });
    if (res.data && res.data.errCode === 0) {
      const list = res.data.data.list || [];
      collegesList.value = list;
      const map = {};
      list.forEach(c => {
        map[c.college_id] = c.college_name;
      });
      collegesMap.value = map;
    }
  } catch (err) {
    console.error('Fetch colleges failed', err);
  }
};

const fetchPendingCourses = async () => {
  isLoading.value = true;
  try {
    const res = await api.post('/review/get_course_list', {
      base: getBase(),
      college_id: '0',
      status: 2, // 2 = 待审核
      page: 1,
      page_size: 500
    });
    if (res.data && res.data.errCode === 0) {
      pendingCourses.value = res.data.data.list || [];
    } else {
      showToast(res.data?.errMsg || '获取待审核课程失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  } finally {
    isLoading.value = false;
  }
};

const fetchAllCourses = async () => {
  try {
    const res = await api.post('/review/get_course_list', {
      base: getBase(),
      college_id: '0',
      status: 1, // 1 = 已通过/正常
      page: 1,
      page_size: 1000
    });
    if (res.data && res.data.errCode === 0) {
      coursesList.value = res.data.data.list || [];
    }
  } catch (err) {
    console.error('Fetch courses failed', err);
  }
};

const handleApprove = async (courseId) => {
  if (!confirm('确定要通过这个课程申请吗？')) return;
  
  try {
    const res = await api.post('/review/approve_course', {
      base: getBase(),
      course_id: String(courseId)
    });
    if (res.data && res.data.errCode === 0) {
      showToast('审核通过！', 'success');
      await fetchPendingCourses();
      await fetchAllCourses();
    } else {
      showToast(res.data?.errMsg || '审核失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const handleReject = async (courseId) => {
  if (!confirm('确定要拒绝这个课程申请吗？拒绝后该记录将被删除。')) return;
  
  try {
    const res = await api.post('/review/reject_course', {
      base: getBase(),
      course_id: String(courseId)
    });
    if (res.data && res.data.errCode === 0) {
      showToast('已拒绝申请！', 'success');
      await fetchPendingCourses();
    } else {
      showToast(res.data?.errMsg || '操作失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const getCollegeName = (id) => {
  if (id === '0' || id === 0 || !id) return '全校公共';
  return collegesMap.value[id] || '未知学院';
};

const getCourseName = (id) => {
  let course = coursesList.value.find(c => c.course_id == id);
  if (!course) {
    course = pendingCourses.value.find(c => c.course_id == id);
  }
  if (course) {
    const college = getCollegeName(course.college_id);
    return `${college} - ${course.course_name}`;
  }
  return `课程ID: ${id} (all:${coursesList.value.length} pending:${pendingCourses.value.length})`;
};

// College CRUD
const openAddCollege = () => {
  editingCollege.value = null;
  collegeForm.value = { college_name: '', college_code: '', description: '' };
  showCollegeModal.value = true;
};

const openEditCollege = (college) => {
  editingCollege.value = college;
  collegeForm.value = { ...college };
  showCollegeModal.value = true;
};

const saveCollege = async () => {
  if (!collegeForm.value.college_name) return showToast('请输入学院名称', 'warning');
  
  const url = editingCollege.value ? '/review/update_college' : '/review/add_college';
  const payload = editingCollege.value ? {
    base: getBase(),
    college_id: String(editingCollege.value.college_id),
    ...collegeForm.value
  } : {
    base: getBase(),
    ...collegeForm.value
  };

  try {
    const res = await api.post(url, payload);
    if (res.data && res.data.errCode === 0) {
      showToast(editingCollege.value ? '修改成功' : '添加成功', 'success');
      showCollegeModal.value = false;
      await fetchColleges();
    } else {
      showToast(res.data?.errMsg || '操作失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const deleteCollege = async (id) => {
  if (!confirm('确定要删除该学院吗？')) return;
  try {
    const res = await api.post('/review/delete_college', { base: getBase(), college_id: String(id) });
    if (res.data && res.data.errCode === 0) {
      showToast('删除成功', 'success');
      await fetchColleges();
    } else {
      showToast(res.data?.errMsg || '删除失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const viewFile = async (fileKey) => {
  try {
    const res = await api.post('/bmanager/get_image_url', {
      base: getBase(),
      image_key: fileKey
    });
    if (res.data && res.data.errCode === 0 && res.data.data && res.data.data.url) {
      window.open(res.data.data.url, '_blank');
    } else {
      showToast(res.data?.errMsg || '获取文件下载链接失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

// Course CRUD
const openAddCourse = () => {
  editingCourse.value = null;
  courseForm.value = { course_name: '', college_id: '0', course_category: '' };
  showCourseModal.value = true;
};

const openEditCourse = (course) => {
  editingCourse.value = course;
  courseForm.value = { ...course, college_id: String(course.college_id || '0') };
  showCourseModal.value = true;
};

const saveCourse = async () => {
  if (!courseForm.value.course_name) return showToast('请输入课程名称', 'warning');
  
  const url = editingCourse.value ? '/review/update_course' : '/review/add_course';
  const payload = editingCourse.value ? {
    base: getBase(),
    course_id: String(editingCourse.value.course_id),
    course_name: courseForm.value.course_name,
    college_id: courseForm.value.college_id == '0' ? '0' : String(courseForm.value.college_id),
    course_category: courseForm.value.course_category
  } : {
    base: getBase(),
    course_name: courseForm.value.course_name,
    college_id: courseForm.value.college_id == '0' ? '0' : String(courseForm.value.college_id),
    course_category: courseForm.value.course_category
  };

  try {
    const res = await api.post(url, payload);
    if (res.data && res.data.errCode === 0) {
      showToast(editingCourse.value ? '修改成功' : '添加成功', 'success');
      showCourseModal.value = false;
      await fetchAllCourses();
    } else {
      showToast(res.data?.errMsg || '操作失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const deleteCourse = async (id) => {
  if (!confirm('确定要删除该课程吗？')) return;
  try {
    const res = await api.post('/review/delete_course', { base: getBase(), course_id: String(id) });
    if (res.data && res.data.errCode === 0) {
      showToast('删除成功', 'success');
      await fetchAllCourses();
    } else {
      showToast(res.data?.errMsg || '删除失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

// --- Upload Reviews ---
const fetchUploadTasks = async () => {
  try {
    const res = await api.post('/review/get_upload_task_list', {
      base: getBase(),
      page: 1,
      page_size: 100
    });
    if (res.data && res.data.errCode === 0) {
      uploadTasks.value = res.data.data.list || [];
    }
  } catch (err) {
    console.error('Fetch upload tasks failed', err);
  }
};

const viewTaskFiles = async (taskId) => {
  currentTaskId.value = taskId;
  uploadFiles.value = [];
  showFilesModal.value = true;
  try {
    const res = await api.post('/review/get_upload_task_files', {
      base: getBase(),
      task_id: String(taskId)
    });
    if (res.data && res.data.errCode === 0) {
      uploadFiles.value = res.data.data.list || [];
    }
  } catch (err) {
    showToast('获取文件失败', 'error');
  }
};

const updateFileStatus = async (fileId, status) => {
  try {
    const res = await api.post('/review/update_file_approve_status', {
      base: getBase(),
      file_id: String(fileId),
      status: status
    });
    if (res.data && res.data.errCode === 0) {
      showToast('审核操作成功', 'success');
      await viewTaskFiles(currentTaskId.value); // refresh files
    } else {
      showToast(res.data?.errMsg || '操作失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const getFileTypeName = (type) => {
  switch (type) {
    case 1: return '重点资料';
    case 2: return '内容资料';
    case 3: return '真题试卷';
    default: return '未知';
  }
};
</script>

<template>
  <div class="admin-container">
    <div class="header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        返回应用中心
      </button>
      <h1 class="title">课程与学院管理后台</h1>
    </div>
    
    <div class="tabs">
      <button :class="['tab-btn', { active: activeTab === 'pending' }]" @click="switchTab('pending')">待审核申请</button>
      <button :class="['tab-btn', { active: activeTab === 'colleges' }]" @click="switchTab('colleges')">学院管理</button>
      <button :class="['tab-btn', { active: activeTab === 'courses' }]" @click="switchTab('courses')">课程管理</button>
      <button :class="['tab-btn', { active: activeTab === 'reviews' }]" @click="switchTab('reviews')">资料审核</button>
    </div>

    <!-- 资料审核 -->
    <div class="card" v-if="activeTab === 'reviews'">
      <div class="card-header">
        <h2 class="card-title">用户上传资料审核</h2>
        <button class="refresh-btn" @click="fetchUploadTasks">
          刷新
        </button>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>任务 ID</th>
              <th>课程</th>
              <th>提交用户 ID</th>
              <th>上传时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="uploadTasks.length === 0">
              <td colspan="5" class="text-center py-8 text-gray-500">暂无待审核任务</td>
            </tr>
            <tr v-for="task in uploadTasks" :key="task.task_id" v-else>
              <td>{{ task.task_id }}</td>
              <td>{{ task.college_name }} - <span class="font-medium">{{ task.course_name }}</span></td>
              <td>{{ task.user_id }}</td>
              <td>{{ new Date(task.created_at).toLocaleString() }}</td>
              <td class="action-cell">
                <button class="primary-btn" @click="viewTaskFiles(task.task_id)">查看文件</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 待审核申请 -->
    <div class="card" v-if="activeTab === 'pending'">
      <div class="card-header">
        <h2 class="card-title">待审核的课程申请</h2>
        <button class="refresh-btn" @click="fetchPendingCourses" :disabled="isLoading">
          刷新
        </button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>课程</th>
              <th>课程类别</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading">
              <td colspan="6" class="text-center py-8 text-gray-500">加载中...</td>
            </tr>
            <tr v-else-if="pendingCourses.length === 0">
              <td colspan="6" class="text-center py-8 text-gray-500">暂无待审核课程</td>
            </tr>
            <tr v-for="course in pendingCourses" :key="course.course_id" v-else>
              <td>{{ getCollegeName(course.college_id) }} - <span class="font-medium">{{ course.course_name }}</span></td>
              <td>
                <span class="category-badge">{{ course.course_category }}</span>
              </td>
              <td>
                <span class="status-badge pending">待审核</span>
              </td>
              <td class="action-cell">
                <button class="approve-btn" @click="handleApprove(course.course_id)">同意</button>
                <button class="reject-btn" @click="handleReject(course.course_id)">拒绝</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 学院管理 -->
    <div class="card" v-if="activeTab === 'colleges'">
      <div class="card-header">
        <h2 class="card-title">学院列表</h2>
        <button class="primary-btn" @click="openAddCollege">新增学院</button>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>学院 ID</th>
              <th>名称</th>
              <th>代码</th>
              <th>描述</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="collegesList.length === 0">
              <td colspan="5" class="text-center py-8 text-gray-500">暂无学院</td>
            </tr>
            <tr v-for="col in collegesList" :key="col.college_id" v-else>
              <td>{{ col.college_id }}</td>
              <td class="font-medium">{{ col.college_name }}</td>
              <td>{{ col.college_code }}</td>
              <td>{{ col.description }}</td>
              <td class="action-cell">
                <button class="edit-btn" @click="openEditCollege(col)">编辑</button>
                <button class="delete-btn" @click="deleteCollege(col.college_id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 课程管理 -->
    <div class="card" v-if="activeTab === 'courses'">
      <div class="card-header">
        <h2 class="card-title">课程列表</h2>
        <button class="primary-btn" @click="openAddCourse">新增课程</button>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>课程</th>
              <th>类别</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="coursesList.length === 0">
              <td colspan="5" class="text-center py-8 text-gray-500">暂无课程</td>
            </tr>
            <tr v-for="course in coursesList" :key="course.course_id" v-else>
              <td>{{ getCollegeName(course.college_id) }} - <span class="font-medium">{{ course.course_name }}</span></td>
              <td><span class="category-badge">{{ course.course_category }}</span></td>
              <td class="action-cell">
                <button class="edit-btn" @click="openEditCourse(course)">编辑</button>
                <button class="delete-btn" @click="deleteCourse(course.course_id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 学院表单弹窗 -->
    <div class="modal-overlay" v-if="showCollegeModal" @click.self="showCollegeModal = false">
      <div class="modal-content">
        <h3>{{ editingCollege ? '编辑学院' : '新增学院' }}</h3>
        <div class="form-group">
          <label>学院名称</label>
          <input type="text" v-model="collegeForm.college_name" placeholder="请输入学院名称" />
        </div>
        <div class="form-group">
          <label>学院代码</label>
          <input type="text" v-model="collegeForm.college_code" placeholder="如：CS" />
        </div>
        <div class="form-group">
          <label>描述</label>
          <textarea v-model="collegeForm.description" placeholder="简单描述"></textarea>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showCollegeModal = false">取消</button>
          <button class="primary-btn" @click="saveCollege">保存</button>
        </div>
      </div>
    </div>

    <!-- 课程表单弹窗 -->
    <div class="modal-overlay" v-if="showCourseModal" @click.self="showCourseModal = false">
      <div class="modal-content">
        <h3>{{ editingCourse ? '编辑课程' : '新增课程' }}</h3>
        <div class="form-group">
          <label>课程名称</label>
          <input type="text" v-model="courseForm.course_name" placeholder="请输入课程名称" />
        </div>
        <div class="form-group">
          <label>所属学院</label>
          <select v-model="courseForm.college_id">
            <option value="0">全校公选</option>
            <option v-for="col in collegesList" :key="col.college_id" :value="col.college_id">{{ col.college_name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>课程类别</label>
          <input type="text" v-model="courseForm.course_category" placeholder="如：必修、选修等" />
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showCourseModal = false">取消</button>
          <button class="primary-btn" @click="saveCourse">保存</button>
        </div>
      </div>
    </div>

    <!-- 文件审核弹窗 -->
    <div class="modal-overlay" v-if="showFilesModal" @click.self="showFilesModal = false">
      <div class="modal-content" style="max-width: 800px; width: 90%;">
        <h3>任务 [{{ currentTaskId }}] 文件列表</h3>
        <div class="table-container" style="max-height: 400px; overflow-y: auto;">
          <table class="data-table">
            <thead>
              <tr>
                <th>文件类型</th>
                <th>文件名/地址</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="uploadFiles.length === 0">
                <td colspan="4" class="text-center py-8 text-gray-500">该任务下暂无文件记录</td>
              </tr>
              <tr v-for="file in uploadFiles" :key="file.file_id" v-else>
                <td>{{ getFileTypeName(file.file_type) }}</td>
                <td style="word-break: break-all;">
                  {{ file.file_key }}
                </td>
                <td>
                  <span class="status-badge" :class="{'pending': (file.approve_status || 0) === 0, 'success': file.approve_status === 1, 'rejected': file.approve_status === 2, 'summarized': file.approve_status === 3}"
                        :style="file.approve_status === 1 ? 'background: rgba(16,185,129,0.1); color: #10b981;' : (file.approve_status === 2 ? 'background: rgba(239,68,68,0.1); color: #ef4444;' : (file.approve_status === 3 ? 'background: rgba(59,130,246,0.1); color: #3b82f6;' : ''))">
                    {{ (file.approve_status || 0) === 0 ? '待审核' : (file.approve_status === 1 ? '已通过' : (file.approve_status === 2 ? '已驳回' : (file.approve_status === 3 ? '已归纳' : '未知状态'))) }}
                  </span>
                </td>
                <td class="action-cell">
                  <button class="view-btn" @click="viewFile(file.file_key)">查看</button>
                  <button class="approve-btn" @click="updateFileStatus(file.file_id, 1)" v-if="(file.approve_status || 0) !== 1">通过</button>
                  <button class="reject-btn" @click="updateFileStatus(file.file_id, 2)" v-if="(file.approve_status || 0) !== 2">驳回</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="modal-actions">
          <button class="primary-btn" @click="showFilesModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}
.header {
  margin-bottom: 20px;
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
.tabs {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}
.tab-btn {
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  opacity: 0.6;
  padding: 8px 16px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.tab-btn:hover {
  opacity: 0.8;
}
.tab-btn.active {
  opacity: 1;
  border-bottom-color: #3b82f6;
  color: #3b82f6;
}
.card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.card-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}
.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-color);
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.refresh-btn:hover:not(:disabled) {
  background: rgba(128, 128, 128, 0.1);
}
.primary-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.primary-btn:hover {
  opacity: 0.9;
}
.table-container {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.data-table th {
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-color);
  color: var(--text-color);
  opacity: 0.8;
  font-weight: 600;
  font-size: 14px;
}
.data-table td {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
  font-size: 14px;
  vertical-align: middle;
}
.font-medium {
  font-weight: 500;
}
.text-center {
  text-align: center;
}
.py-8 {
  padding-top: 32px;
  padding-bottom: 32px;
}
.text-gray-500 {
  opacity: 0.5;
}
.category-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 16px;
  background: rgba(128, 128, 128, 0.1);
  font-size: 12px;
}
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}
.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}
.action-cell {
  display: flex;
  gap: 8px;
}
.view-btn, .approve-btn, .reject-btn, .edit-btn, .delete-btn {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}
.view-btn {
  background: #3b82f6;
  color: white;
}
.view-btn:hover {
  opacity: 0.9;
}
.approve-btn {
  background: #10b981;
  color: white;
}
.approve-btn:hover {
  opacity: 0.9;
}
.reject-btn {
  background: transparent;
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.5);
}
.reject-btn:hover {
  background: #ef4444;
  color: white;
}
.edit-btn {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}
.edit-btn:hover {
  background: #3b82f6;
  color: white;
}
.delete-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}
.delete-btn:hover {
  background: #ef4444;
  color: white;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: var(--bg-color);
  padding: 24px;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
}
.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
  color: var(--text-color);
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--text-color);
  opacity: 0.8;
}
.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: transparent;
  color: var(--text-color);
  font-size: 14px;
}
.form-group textarea {
  resize: vertical;
  min-height: 80px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
.cancel-btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  border-radius: 8px;
  cursor: pointer;
}
.cancel-btn:hover {
  background: rgba(128,128,128,0.1);
}
</style>
