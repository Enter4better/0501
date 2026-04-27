<template>
  <el-card shadow="hover" class="tech-card">
    <template #header>
      <div class="card-header">
        <span class="card-title"><el-icon><List /></el-icon> 攻击队列</span>
        <el-button text type="danger" size="small" @click="clearQueue" :disabled="queue.length === 0">
          清空队列
        </el-button>
      </div>
    </template>
    <div v-if="queue.length === 0" class="empty-queue">
      <el-icon><Box /></el-icon>
      <p>暂无待执行的攻击任务</p>
    </div>
    <div v-else class="queue-list">
      <div v-for="(task, index) in queue" :key="task.id" class="queue-item">
        <div class="queue-info">
          <span class="queue-name">{{ task.name }}</span>
          <el-tag size="small" :type="getStatusType(task.status)">{{ task.status }}</el-tag>
        </div>
        <div class="queue-actions">
          <el-button 
            v-if="task.status === 'pending'" 
            text 
            type="danger" 
            size="small"
            @click="removeTask(task.id)"
          >
            取消
          </el-button>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { List, Box } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  queue: { type: Array, default: () => [] }
})

const emit = defineEmits(['clear', 'remove'])

function getStatusType(status) {
  const typeMap = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

function clearQueue() {
  emit('clear')
  ElMessage.success('队列已清空')
}

function removeTask(id) {
  emit('remove', id)
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-display) !important;
}

.empty-queue {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-muted);
}

.empty-queue .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.queue-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.queue-name {
  font-size: 14px;
  color: var(--text-primary);
  font-family: var(--font-ui) !important;
}
</style>