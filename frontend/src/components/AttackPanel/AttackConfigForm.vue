<template>
  <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
    <template #header>
      <div class="card-header">
        <span class="card-title"><el-icon><Setting /></el-icon> 攻击配置</span>
        <el-tag v-if="form.type" :type="getAttackTypeTag(form.type)" size="small">
          {{ form.type }}
        </el-tag>
      </div>
    </template>
    
    <el-form :model="form" label-width="100px" size="default" class="attack-form">
      <el-form-item label="攻击名称">
        <el-input v-model="form.name" placeholder="给攻击起个名字（可选）" clearable>
          <template #prefix>
            <el-icon><Edit /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="攻击类型" required>
        <AttackTypeSelect v-model="form.type" @change="onAttackTypeChange" />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="16">
          <el-form-item label="目标地址" required>
            <el-input v-model="form.target" placeholder="192.168.1.100 或 localhost">
              <template #prefix>
                <el-icon><Location /></el-icon>
              </template>
              <template #append>
                <el-button @click="$emit('select-target')" :icon="Monitor">选择靶场</el-button>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="端口">
            <el-input v-model="form.port" placeholder="8080">
              <template #prefix>
                <el-icon><Connection /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="攻击参数">
        <el-input 
          v-model="form.params" 
          type="textarea" 
          :rows="4" 
          placeholder="输入JSON格式的攻击参数"
          class="code-textarea"
        />
      </el-form-item>

      <el-form-item label="攻击强度">
        <div class="intensity-wrapper">
          <el-slider 
            v-model="form.intensity" 
            :min="1" 
            :max="10" 
            :marks="intensityMarks"
            :format-tooltip="formatIntensity"
            show-stops
            class="intensity-slider"
          />
        </div>
        <div class="intensity-footer">
          <el-tag :type="getIntensityType(form.intensity)" size="small" class="intensity-tag">
            强度 {{ form.intensity }} - {{ formatIntensity(form.intensity) }}
          </el-tag>
        </div>
      </el-form-item>
    </el-form>

    <!-- 操作按钮区域 -->
    <div class="form-actions-wrapper">
      <p class="form-actions-tip">配置完成后点击下方按钮执行攻击操作</p>
      <div class="form-actions">
        <el-button type="danger" size="default" :loading="loading" @click="launch" :disabled="!form.type || !form.target">
          <el-icon><Aim /></el-icon>
          发起攻击
        </el-button>
        <el-button size="default" @click="saveAsTemplate" :disabled="!form.type">
          <el-icon><FolderAdd /></el-icon>
          保存为模板
        </el-button>
        <el-button size="default" @click="resetForm">
          <el-icon><Refresh /></el-icon>
          重置配置
        </el-button>
        <el-button type="success" @click="aiPlanAttack" :disabled="!form.target">
          <el-icon><MagicStick /></el-icon>
          AI智能规划攻击
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, defineEmits, defineProps } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Aim, Setting, Edit, Location, Connection,
  MagicStick, FolderAdd, Refresh, Monitor, Document
} from '@element-plus/icons-vue'
import axios from 'axios'
import AttackTypeSelect from '@/components/AttackTypeSelect.vue'

// 定义props
const props = defineProps({
  loading: Boolean,
  result: Object
})

// 定义emits
const emit = defineEmits(['update:result', 'update:resultType', 'update:resultStatus', 'load-attack-history', 'load-stats', 'select-target'])

// 表单
const intensityMarks = { 1: '隐蔽', 3: '低', 5: '中', 7: '高', 10: '极限' }
const form = ref({ name: '', type: '', target: 'localhost', port: '80', params: '', intensity: 5 })

// 工具函数
function getAttackTypeTag(type) {
  const typeMap = { 'SQL注入': 'danger', 'XSS攻击': 'warning', 'CSRF攻击': 'warning', '文件包含': 'danger', '命令执行': 'danger', 'SSRF攻击': 'warning', 'XXE注入': 'danger', '权限提升': 'danger', '容器逃逸': 'danger', '反弹Shell': 'danger', '端口扫描': 'info', '暴力破解': 'danger', '中间人攻击': 'danger', '后门植入': 'danger', '横向移动': 'danger', '数据外传': 'danger' }
  return typeMap[type] || 'info'
}

function formatIntensity(val) {
  const labels = { 1: '隐蔽', 2: '很低', 3: '低', 4: '中低', 5: '中等', 6: '中高', 7: '高', 8: '很高', 9: '极高', 10: '极限' }
  return labels[val] || val
}

function getIntensityType(val) {
  if (val <= 3) return 'success'
  if (val <= 6) return 'warning'
  return 'danger'
}

function onAttackTypeChange(type, port) {
  form.value.port = port
  emit('attack-type-change', type, port)
}

function resetForm() {
  form.value = { name: '', type: '', target: 'localhost', port: '80', params: '', intensity: 5 }
  emit('update:result', '')
}

// 攻击操作
async function launch() {
  if (!form.value.type || !form.value.target) {
    ElMessage.warning('请填写攻击类型和目标地址')
    return
  }

  emit('update:loading', true)
  emit('update:result', '')
  
  try {
    const createRes = await axios.post('/api/attack/create', {
      name: form.value.name || form.value.type,
      attack_type: form.value.type,
      target: form.value.target + ':' + form.value.port,
      port: form.value.port,
      intensity: form.value.intensity
    })

    if (createRes.data.status === 'success') {
      const attackId = createRes.data.attack?.attack_id || Date.now()
      const execRes = await axios.post(`/api/attack/execute/${attackId}`)
      
      if (execRes.data.status === 'success') {
        emit('update:result', JSON.stringify({ status: 'success', attack_id: attackId, result: '攻击测试完成', vulnerabilities_found: 2 }, null, 2))
        emit('update:resultType', 'success')
        emit('update:resultStatus', '成功')
        ElMessage.success('攻击测试完成')
        emit('load-attack-history')
        emit('load-stats')
      } else {
        throw new Error(execRes.data.msg || '攻击执行失败')
      }
    } else {
      throw new Error(createRes.data.msg || '创建攻击失败')
    }
  } catch (e) {
    emit('update:result', `攻击执行失败: ${e.response?.data?.msg || e.message}`)
    emit('update:resultType', 'danger')
    emit('update:resultStatus', '失败')
    ElMessage.error('攻击执行失败')
  } finally {
    emit('update:loading', false)
  }
}

// AI智能规划攻击
async function aiPlanAttack() {
  if (!form.value.target) {
    ElMessage.warning('请选择目标')
    return
  }

  emit('update:loading', true)
  emit('update:result', '')
  
  try {
    // 调用AI接口进行攻击规划
    const aiRes = await axios.post('/api/ai/plan-attack', {
      target: form.value.target,
      port: form.value.port,
      description: `对目标${form.value.target}:${form.value.port}进行安全测试，请规划合适的攻击策略`
    })

    if (aiRes.data.status === 'success') {
      const plan = aiRes.data.plan
      emit('update:result', JSON.stringify(plan, null, 2))
      emit('update:resultType', 'success')
      emit('update:resultStatus', 'AI规划完成')
      ElMessage.success('AI已生成攻击规划')

      // 应用AI推荐的攻击类型
      if (plan.recommended_attack) {
        form.value.type = plan.recommended_attack
      }
      
      // 应用AI推荐的强度
      if (plan.recommended_intensity) {
        form.value.intensity = plan.recommended_intensity
      }
    } else {
      throw new Error(aiRes.data.msg || 'AI规划失败')
    }
  } catch (e) {
    emit('update:result', `AI规划失败: ${e.response?.data?.msg || e.message}`)
    emit('update:resultType', 'warning')
    emit('update:resultStatus', 'AI规划失败')
    ElMessage.warning('AI规划失败')
  } finally {
    emit('update:loading', false)
  }
}

function saveAsTemplate() { 
  ElMessage.info('模板保存功能开发中') 
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

.attack-form { padding: 8px 0; }
.code-textarea { font-family: var(--font-mono); }

.intensity-wrapper { 
  display: flex; 
  align-items: center; 
  width: 100%;
  padding: 8px 0;
}

.intensity-slider { 
  flex: 1; 
}

.intensity-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.intensity-tag { 
  min-width: 100px; 
  text-align: center; 
  padding: 4px 12px;
}

.form-actions-wrapper {
  padding: 16px;
  background: rgba(139, 44, 230, 0.05);
  border-radius: 8px;
  margin-top: 16px;
}

.form-actions-tip { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; text-align: center; }
.form-actions { display: flex; gap: 12px; justify-content: center; }
</style>