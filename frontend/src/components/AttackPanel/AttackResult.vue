<template>
  <el-card shadow="hover" class="tech-card" v-if="result">
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Document /></el-icon>
          攻击结果
        </span>
        <div class="result-actions">
          <el-tag :type="resultType" size="small">{{ resultStatus }}</el-tag>
          <el-button text size="small" @click="copyResult">
            <el-icon><CopyDocument /></el-icon>
            复制
          </el-button>
          <el-button text size="small" @click="closeResult">
            <el-icon><Close /></el-icon>
            关闭
          </el-button>
        </div>
      </div>
    </template>
    <div class="result-content">
      <pre v-html="formatResult(result)"></pre>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, CopyDocument, Close } from '@element-plus/icons-vue'

// 定义props
const props = defineProps({
  result: String,
  resultType: String,
  resultStatus: String
})

// 定义emits
const emit = defineEmits(['update:result'])

function formatResult(text) {
  if (!text) return ''
  return text.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>')
    .replace(/"成功"/g, '<span style="color: #67c23a;">"成功"</span>')
    .replace(/"失败"/g, '<span style="color: #f56c6c;">"失败"</span>')
}

function copyResult() {
  navigator.clipboard.writeText(props.result)
  ElMessage.success('已复制到剪贴板')
}

function closeResult() {
  emit('update:result', '')
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

.result-content {
  background: rgba(0, 0, 0, 0.2);
  padding: 16px;
  border-radius: 8px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-secondary);
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}
</style>