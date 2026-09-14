<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { showToast } from '../utils/toast';

const router = useRouter();

const goBackToApps = () => {
  router.push('/apps');
};

const getBase = () => ({
  access_token: localStorage.getItem('access_token') || '',
  email: localStorage.getItem('user_email') || '',
  user_id: localStorage.getItem('user_id') || '0'
});

const myUserId = computed(() => localStorage.getItem('user_id') || '0');

// View state: 'activities' | 'bills'
const currentView = ref('activities');
const currentActivity = ref(null);
const activityMembers = ref([]);

// Activities Data
const activities = ref([]);
const isFetchingActivities = ref(false);

// Modals
const showCreateActivityModal = ref(false);
const createActivityForm = ref({ name: '', description: '' });

const showJoinActivityModal = ref(false);
const joinActivityForm = ref({ activity_id: '' });

const showCreateBillModal = ref(false);
const createBillForm = ref({ amount: '', description: '', payer_id: '' });

// Edit/Delete Bill Modals
const showEditBillModal = ref(false);
const editBillForm = ref({ bill_id: '', amount: '', description: '', payer_id: '' });

// Bills Data
const bills = ref([]);
const isFetchingBills = ref(false);

onMounted(() => {
  // Try fetching activities
  fetchActivities();
});

const fetchActivities = async () => {
  isFetchingActivities.value = true;
  try {
    const res = await api.post('/group/list_my_activities', { base: getBase(), user_id: myUserId.value });
    if (res.data && res.data.errCode === 0) {
      activities.value = res.data.data.activities || [];
    } else {
      showToast(res.data?.errMsg || '获取活动失败', 'error');
    }
  } catch (err) {
    showToast('获取活动失败', 'error');
  } finally {
    isFetchingActivities.value = false;
  }
};

const enterActivity = (activity) => {
  currentActivity.value = activity;
  currentView.value = 'bills';
  fetchBills(activity.activity_id);
  fetchMembers(activity.activity_id);
};

const leaveActivity = () => {
  currentActivity.value = null;
  currentView.value = 'activities';
  activityMembers.value = [];
};

const fetchMembers = async (activityId) => {
  try {
    const res = await api.post('/group/get_activity_members', { base: getBase(), activity_id: activityId });
    if (res.data && res.data.errCode === 0) {
      const members = res.data.data.members || [];
      const userIds = members.map(m => m.user_id);
      
      if (userIds.length > 0) {
        const infoRes = await api.post('/user/get_users_info', { base: getBase(), user_ids: userIds });
        if (infoRes.data && infoRes.data.errCode === 0) {
          const nicknames = infoRes.data.data.nicknames || {};
          activityMembers.value = members.map(m => ({
            user_id: m.user_id,
            nickname: nicknames[m.user_id] || `用户${m.user_id}`
          }));
        } else {
          activityMembers.value = members.map(m => ({ user_id: m.user_id, nickname: `用户${m.user_id}` }));
        }
      } else {
        activityMembers.value = [];
      }
    }
  } catch (err) {
    console.error('获取成员失败', err);
  }
};

const fetchBills = async (activityId) => {
  isFetchingBills.value = true;
  try {
    const res = await api.post('/group/list_bills', {
      base: getBase(),
      activity_id: activityId,
      user_id: myUserId.value
    });
    if (res.data && res.data.errCode === 0) {
      bills.value = res.data.data.bills || [];
    } else {
      showToast(res.data?.errMsg || '获取账单失败', 'error');
    }
  } catch (err) {
    showToast('获取账单失败', 'error');
  } finally {
    isFetchingBills.value = false;
  }
};

const formatMoney = (cents) => {
  return (cents / 100).toFixed(2);
};

const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${month}-${day} ${hours}:${minutes}`;
};

const memberSpends = computed(() => {
  const spends = {};
  activityMembers.value.forEach(m => {
    spends[m.user_id] = { user_id: m.user_id, nickname: m.nickname, total: 0 };
  });
  bills.value.forEach(b => {
    if (!spends[b.payer_id]) {
      spends[b.payer_id] = { user_id: b.payer_id, nickname: `用户${b.payer_id}`, total: 0 };
    }
    spends[b.payer_id].total += b.amount;
  });
  return Object.values(spends).sort((a, b) => b.total - a.total);
});

// Actions
const submitCreateActivity = async () => {
  if (!createActivityForm.value.name) {
    showToast('请输入活动名称', 'warning');
    return;
  }
  try {
    const res = await api.post('/group/create_activity', {
      base: getBase(),
      creator_id: myUserId.value,
      name: createActivityForm.value.name,
      description: createActivityForm.value.description
    });
    if (res.data && res.data.errCode === 0) {
      showToast('活动创建成功', 'success');
      showCreateActivityModal.value = false;
      fetchActivities();
    } else {
      showToast(res.data?.errMsg || '创建失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const submitJoinActivity = async () => {
  if (!joinActivityForm.value.activity_id) {
    showToast('请输入活动ID', 'warning');
    return;
  }
  try {
    const res = await api.post('/group/apply_join_activity', {
      base: getBase(),
      user_id: myUserId.value,
      activity_id: joinActivityForm.value.activity_id
    });
    if (res.data && res.data.errCode === 0) {
      showToast('申请成功，请等待房主审批', 'success');
      showJoinActivityModal.value = false;
    } else {
      showToast(res.data?.errMsg || '申请失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const submitCreateBill = async () => {
  if (!createBillForm.value.amount || !createBillForm.value.description) {
    showToast('金额和描述不能为空', 'warning');
    return;
  }
  try {
    const amountInCents = Math.round(parseFloat(createBillForm.value.amount) * 100);
    const res = await api.post('/group/create_bill', {
      base: getBase(),
      activity_id: currentActivity.value.activity_id,
      amount: amountInCents,
      description: createBillForm.value.description,
      payer_id: createBillForm.value.payer_id || myUserId.value,
      creator_id: myUserId.value
    });
    if (res.data && res.data.errCode === 0) {
      showToast('记账成功', 'success');
      showCreateBillModal.value = false;
      fetchBills(currentActivity.value.activity_id);
    } else {
      showToast(res.data?.errMsg || '记账失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const openEditBillModal = (bill) => {
  editBillForm.value = {
    bill_id: bill.bill_id,
    amount: (bill.amount / 100).toFixed(2),
    description: bill.description,
    payer_id: bill.payer_id,
    creator_id: bill.creator_id
  };
  showEditBillModal.value = true;
};

const submitEditBill = async () => {
  if (!editBillForm.value.amount || !editBillForm.value.description) {
    showToast('金额和描述不能为空', 'warning');
    return;
  }
  try {
    const amountInCents = Math.round(parseFloat(editBillForm.value.amount) * 100);
    const res = await api.post('/group/update_bill', {
      base: getBase(),
      bill_id: editBillForm.value.bill_id,
      operator_id: myUserId.value,
      amount: amountInCents,
      description: editBillForm.value.description,
      payer_id: editBillForm.value.payer_id
    });
    if (res.data && res.data.errCode === 0) {
      showToast('修改成功', 'success');
      showEditBillModal.value = false;
      fetchBills(currentActivity.value.activity_id);
    } else {
      showToast(res.data?.errMsg || '修改失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const submitDeleteBill = async () => {
  if (!confirm('确定要删除这笔账单吗？')) {
    return;
  }
  try {
    const res = await api.post('/group/delete_bill', {
      base: getBase(),
      bill_id: editBillForm.value.bill_id,
      operator_id: myUserId.value
    });
    if (res.data && res.data.errCode === 0) {
      showToast('删除成功', 'success');
      showEditBillModal.value = false;
      fetchBills(currentActivity.value.activity_id);
    } else {
      showToast(res.data?.errMsg || '删除失败', 'error');
    }
  } catch (err) {
    showToast('网络异常', 'error');
  }
};

const copyActivityId = (id) => {
  if (!id) return;
  navigator.clipboard.writeText(id).then(() => {
    showToast('活动ID已复制到剪贴板', 'success');
  }).catch(() => {
    showToast('复制失败，请手动复制', 'error');
  });
};

</script>

<template>
  <div class="group-accounting-container">
    <div class="header">
      <button class="back-btn" @click="currentView === 'bills' ? leaveActivity() : goBackToApps()">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        {{ currentView === 'bills' ? '返回活动列表' : '返回应用中心' }}
      </button>
      <h1 class="title">{{ currentView === 'bills' ? currentActivity?.name : '群组记账' }}</h1>
    </div>

    <!-- Activities View -->
    <div v-show="currentView === 'activities'">
      <div class="actions-row">
        <button class="primary-btn" @click="showCreateActivityModal = true">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          创建新活动
        </button>
        <button class="secondary-btn" @click="showJoinActivityModal = true">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
          加入活动
        </button>
      </div>

      <div v-if="isFetchingActivities" class="loading-state">加载中...</div>
      <div v-else-if="activities.length === 0" class="empty-state">
        <p>你还没有参与任何活动，快去创建或加入一个吧！</p>
      </div>
      <div v-else class="activities-grid">
        <div v-for="act in activities" :key="act.activity_id" class="activity-card" @click="enterActivity(act)">
          <div class="act-icon">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
          </div>
          <div class="act-info">
            <h3>{{ act.name }}</h3>
            <p>{{ act.description || '暂无描述' }}</p>
            <span class="act-tag" v-if="act.creator_id === myUserId">我创建的</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bills View -->
    <div v-show="currentView === 'bills'">
      <div class="bills-header-actions">
        <div class="activity-meta">
          <p class="activity-desc">{{ currentActivity?.description }}</p>
          <p class="activity-id-display" @click="copyActivityId(currentActivity?.activity_id)">
            活动ID: <span class="id-text">{{ currentActivity?.activity_id }}</span>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-left: 4px; vertical-align: text-bottom;"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
          </p>
        </div>
        <button class="primary-btn sm-btn" @click="showCreateBillModal = true; createBillForm.payer_id = myUserId.value;">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          记一笔
        </button>
      </div>

      <!-- Member Stats -->
      <div class="member-stats-container" v-if="bills.length > 0">
        <h3 class="stats-title">成员消费统计</h3>
        <div class="stats-grid">
          <div v-for="stat in memberSpends" :key="stat.user_id" class="stat-card">
            <div class="stat-name">{{ stat.nickname }}</div>
            <div class="stat-amount">¥{{ formatMoney(stat.total) }}</div>
          </div>
        </div>
      </div>

      <div class="bills-list-container">
        <div v-if="isFetchingBills" class="loading-state">加载账单中...</div>
        <div v-else-if="bills.length === 0" class="empty-state">
          <p>当前活动还没有账单记录</p>
        </div>
        <div v-else class="bills-list">
          <div v-for="bill in bills" :key="bill.bill_id" class="bill-item" @click="openEditBillModal(bill)">
            <div class="bill-icon">
              <!-- Random color icon based on description length for variety -->
              <div class="icon-circle" :style="{'background-color': bill.description.length % 2 === 0 ? '#e0f2fe' : '#fce7f3', 'color': bill.description.length % 2 === 0 ? '#0284c7' : '#db2777'}">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="2" y="5" width="20" height="14" rx="2"></rect>
                  <line x1="2" y1="10" x2="22" y2="10"></line>
                </svg>
              </div>
            </div>
            <div class="bill-content">
              <div class="bill-top">
                <span class="bill-title">{{ bill.description }}</span>
                <span class="bill-amount" :class="{'my-expense': bill.payer_id === myUserId}">
                  {{ bill.payer_id === myUserId ? '-' : '' }} ¥{{ formatMoney(bill.amount) }}
                </span>
              </div>
              <div class="bill-bottom">
                <span class="bill-time">{{ formatDate(bill.created_at) }}</span>
                <span class="bill-payer">{{ activityMembers.find(m => m.user_id === bill.payer_id)?.nickname || (bill.payer_id === myUserId ? '我付款' : `用户${bill.payer_id}`) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Activity Modal -->
    <div v-if="showCreateActivityModal" class="modal-overlay" @click.self="showCreateActivityModal = false">
      <div class="modal-content">
        <h3 class="modal-title">创建新活动</h3>
        <div class="form-group">
          <label class="form-label">活动名称</label>
          <input v-model="createActivityForm.name" type="text" class="text-input" placeholder="例如：周末成都游">
        </div>
        <div class="form-group">
          <label class="form-label">活动描述</label>
          <textarea v-model="createActivityForm.description" class="text-input" rows="2" placeholder="简单描述一下"></textarea>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showCreateActivityModal = false">取消</button>
          <button class="confirm-btn" @click="submitCreateActivity">创建</button>
        </div>
      </div>
    </div>

    <!-- Join Activity Modal -->
    <div v-if="showJoinActivityModal" class="modal-overlay" @click.self="showJoinActivityModal = false">
      <div class="modal-content">
        <h3 class="modal-title">加入活动</h3>
        <div class="form-group">
          <label class="form-label">活动 ID</label>
          <input v-model="joinActivityForm.activity_id" type="text" class="text-input" placeholder="请输入房主分享的活动ID">
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showJoinActivityModal = false">取消</button>
          <button class="confirm-btn" @click="submitJoinActivity">申请加入</button>
        </div>
      </div>
    </div>

    <!-- Create Bill Modal -->
    <div v-if="showCreateBillModal" class="modal-overlay" @click.self="showCreateBillModal = false">
      <div class="modal-content">
        <h3 class="modal-title">记一笔开销</h3>
        <div class="form-group">
          <label class="form-label">金额 (元)</label>
          <input v-model="createBillForm.amount" type="number" step="0.01" class="text-input" placeholder="0.00">
        </div>
        <div class="form-group">
          <label class="form-label">消费描述</label>
          <input v-model="createBillForm.description" type="text" class="text-input" placeholder="例如：午饭">
        </div>
        <div class="form-group">
          <label class="form-label">付款人</label>
          <select v-model="createBillForm.payer_id" class="text-input">
            <option v-for="m in activityMembers" :key="m.user_id" :value="m.user_id">
              {{ m.nickname }} {{ m.user_id === myUserId ? '(我)' : '' }}
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showCreateBillModal = false">取消</button>
          <button class="confirm-btn" @click="submitCreateBill">保存</button>
        </div>
      </div>
    </div>

    <!-- Edit/Delete Bill Modal -->
    <div v-if="showEditBillModal" class="modal-overlay" @click.self="showEditBillModal = false">
      <div class="modal-content">
        <h3 class="modal-title">编辑账单</h3>
        <div class="form-group">
          <label class="form-label">金额 (元)</label>
          <input v-model="editBillForm.amount" type="number" step="0.01" class="text-input" placeholder="0.00">
        </div>
        <div class="form-group">
          <label class="form-label">消费描述</label>
          <input v-model="editBillForm.description" type="text" class="text-input" placeholder="例如：午饭">
        </div>
        <div class="form-group">
          <label class="form-label">付款人</label>
          <select v-model="editBillForm.payer_id" class="text-input">
            <option v-for="m in activityMembers" :key="m.user_id" :value="m.user_id">
              {{ m.nickname }} {{ m.user_id === myUserId ? '(我)' : '' }}
            </option>
          </select>
        </div>
        <div class="modal-actions" style="justify-content: space-between;">
          <button class="delete-btn" @click="submitDeleteBill">删除</button>
          <div>
            <button class="cancel-btn" style="margin-right: 12px;" @click="showEditBillModal = false">取消</button>
            <button class="confirm-btn" @click="submitEditBill">保存</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.group-accounting-container {
  max-width: 800px;
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

.actions-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.primary-btn, .secondary-btn, .confirm-btn, .cancel-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.primary-btn, .confirm-btn {
  background: var(--text-color);
  color: var(--bg-color);
}

.primary-btn:hover, .confirm-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.secondary-btn {
  background: rgba(128, 128, 128, 0.1);
  color: var(--text-color);
}

.secondary-btn:hover {
  background: rgba(128, 128, 128, 0.15);
}

.cancel-btn {
  background: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.delete-btn {
  background: #fef2f2;
  color: #ef4444;
  border: 1px solid #fca5a5;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #fee2e2;
}

:root[data-theme='dark'] .delete-btn {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
}

:root[data-theme='dark'] .delete-btn:hover {
  background: rgba(239, 68, 68, 0.2);
}

.sm-btn {
  padding: 8px 16px;
  font-size: 13px;
}

.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.activity-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.05);
}

.activity-card:hover {
  transform: translateY(-2px);
  border-color: var(--text-color);
  box-shadow: 0 6px 10px -3px rgba(0, 0, 0, 0.1);
}

.act-icon {
  width: 48px;
  height: 48px;
  background: #f0fdf4;
  color: #16a34a;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.act-info h3 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--text-color);
}

.act-info p {
  font-size: 13px;
  color: var(--text-color);
  opacity: 0.6;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.act-tag {
  font-size: 11px;
  background: #eef2ff;
  color: #4f46e5;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

/* Bills UI WeChat/Alipay Style */
.bills-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.activity-desc {
  font-size: 14px;
  opacity: 0.6;
  margin-bottom: 4px;
}

.activity-id-display {
  font-size: 13px;
  color: var(--text-color);
  opacity: 0.8;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: opacity 0.2s;
}

.activity-id-display:hover {
  opacity: 1;
}

.id-text {
  font-family: monospace;
  font-weight: 600;
  margin-left: 4px;
  background: rgba(128, 128, 128, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.bills-list-container {
  background: var(--bg-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

.bills-list {
  display: flex;
  flex-direction: column;
}

.bill-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  gap: 16px;
  border-bottom: 1px solid rgba(128, 128, 128, 0.1);
  transition: background-color 0.2s;
  cursor: pointer;
}

.bill-item:last-child {
  border-bottom: none;
}

.bill-item:active, .bill-item:hover {
  background-color: rgba(128, 128, 128, 0.05);
}

.bill-icon {
  flex-shrink: 0;
}

.icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bill-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bill-top, .bill-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bill-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-color);
}

.bill-amount {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-color);
}

.my-expense {
  color: #000;
}

:root[data-theme='dark'] .my-expense {
  color: #fff;
}

.bill-time, .bill-payer {
  font-size: 12px;
  color: var(--text-color);
  opacity: 0.5;
}

/* Stats UI */
.member-stats-container {
  margin-bottom: 24px;
}

.stats-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text-color);
}

.stats-grid {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.stat-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px 16px;
  min-width: 120px;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stat-name {
  font-size: 13px;
  opacity: 0.7;
  margin-bottom: 4px;
}

.stat-amount {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-color);
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-color);
  border-radius: 16px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  opacity: 0.8;
}

.text-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-color);
  color: var(--text-color);
  font-size: 14px;
  font-family: inherit;
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

.loading-state, .empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--text-color);
  opacity: 0.6;
}

/* Mobile Adjustments */
@media (max-width: 640px) {
  .title {
    font-size: 24px;
  }
  
  .bill-item {
    padding: 12px 16px;
  }
  
  .icon-circle {
    width: 36px;
    height: 36px;
  }
  
  .bill-title {
    font-size: 14px;
  }
  
  .bill-amount {
    font-size: 15px;
  }
}
</style>
