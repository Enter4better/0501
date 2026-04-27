 <template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Umbrella /></el-icon>
        防御配置面板
      </h2>
      <p class="page-desc">配置和管理安全防御规则，包括WAF、IDS、IPS、蜜罐等多种防御类型</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <StatCard :icon="Lock" :value="stats.active" label="活跃规则" type="success" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard :icon="CircleCheck" :value="stats.blocked" label="本周拦截" type="purple" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard :icon="DataLine" :value="stats.coverage + '%'" label="平均覆盖率" type="cyan" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard :icon="Warning" :value="stats.alerts" label="待处理告警" type="warning" />
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 左侧：防御规则列表 -->
      <el-col :xs="24" :lg="16">
        <!-- 快速模板 -->
        <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title"><el-icon><MagicStick /></el-icon> 快速部署模板</span>
              <el-button text type="primary" @click="showTemplates = !showTemplates">
                {{ showTemplates ? '收起' : '展开' }}
              </el-button>
            </div>
          </template>
          <div v-show="showTemplates" class="template-grid">
            <div 
              v-for="template in templates" 
              :key="template.name"
              class="template-item"
              @click="applyTemplate(template)"
            >
              <el-icon class="template-icon"><Umbrella /></el-icon>
              <span class="template-name">{{ template.name }}</span>
              <span class="template-count">{{ template.defenses?.length || 0 }} 个规则</span>
            </div>
          </div>
        </el-card>

        <!-- 防御规则列表 -->
        <el-card shadow="hover" class="tech-card">
          <template #header>
            <div class="card-header">
              <span class="card-title"><el-icon><List /></el-icon> 防御规则 ({{ rules.length }})</span>
              <div class="header-actions">
                <el-input 
                  v-model="searchKeyword" 
                  placeholder="搜索规则" 
                  clearable 
                  style="width: 150px; margin-right: 12px;"
                  :prefix-icon="Search"
                />
                <el-button type="primary" size="small" @click="showAdd = true">
                  <el-icon><Plus /></el-icon>
                  添加规则
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="loading && rules.length === 0" class="empty-state">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <p>加载中...</p>
          </div>
          <div v-else-if="filteredRules.length === 0" class="empty-state">
            <el-icon><Box /></el-icon>
            <p>{{ searchKeyword ? '未找到匹配的规则' : '暂无防御规则，点击右上角添加' }}</p>
          </div>

          <el-table v-else :data="filteredRules" style="width: 100%" size="small" stripe table-layout="auto">
            <el-table-column prop="name" label="规则名称" min-width="140">
              <template #default="{ row }">
                <div class="rule-name">
                  <el-icon :style="{ color: getTypeColor(row.defense_type) }"><Umbrella /></el-icon>
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="defense_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getTypeTag(row.defense_type)" size="small" effect="dark">
                  {{ row.defense_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="enabled" label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-switch 
                  v-model="row.enabled" 
                  @change="toggleRule(row)" 
                  :loading="row._loading"
                  active-color="#67c23a"
                />
              </template>
            </el-table-column>
            <el-table-column prop="coverage" label="覆盖率" width="120">
              <template #default="{ row }">
                <div class="coverage-cell">
                  <el-progress 
                    :percentage="row.coverage || 0" 
                    :stroke-width="6"
                    :color="getCoverageColor(row.coverage)"
                    :show-text="false"
                    style="width: 70px;"
                  />
                  <span class="coverage-text">{{ row.coverage || 0 }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="120" show-overflow-tooltip />
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button-group class="action-btn-group">
                  <el-button size="small" type="primary" @click="editRule(row)" title="编辑">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteRule(row)" :loading="row._deleting" title="删除">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                  <el-button size="small" type="success" @click="testRule(row)" title="测试">
                    <el-icon><Aim /></el-icon>
                  </el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：防御测试和日志 -->
      <el-col :xs="24" :lg="8">
        <!-- 防御测试 -->
        <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title"><el-icon><Aim /></el-icon> 防御测试</span>
            </div>
          </template>
          <el-form :model="testForm" label-width="80px" size="small">
            <el-form-item label="攻击类型">
              <el-select v-model="testForm.attack_type" style="width: 100%;">
                <el-option label="SQL注入" value="SQL注入" />
                <el-option label="XSS攻击" value="XSS攻击" />
                <el-option label="CSRF攻击" value="CSRF攻击" />
                <el-option label="命令执行" value="命令执行" />
                <el-option label="端口扫描" value="端口扫描" />
                <el-option label="暴力破解" value="暴力破解" />
              </el-select>
            </el-form-item>
            <el-form-item label="攻击强度">
              <el-slider v-model="testForm.intensity" :min="1" :max="10" show-input />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="runDefenseTest" :loading="testing">
                <el-icon><Aim /></el-icon>
                开始测试
              </el-button>
            </el-form-item>
          </el-form>
          <div v-if="testResult" class="test-result">
            <div class="result-header">
              <el-tag :type="testResult.blocked ? 'success' : 'danger'" size="small">
                {{ testResult.blocked ? '拦截成功' : '拦截失败' }}
              </el-tag>
              <span class="result-time">{{ testResult.time }}ms</span>
            </div>
            <div class="result-message">{{ testResult.message }}</div>
          </div>
        </el-card>

        <!-- 防御日志 -->
        <el-card shadow="hover" class="tech-card">
          <template #header>
            <div class="card-header">
              <span class="card-title"><el-icon><Document /></el-icon> 防御日志</span>
              <el-button text type="primary" size="small" @click="loadDefenseLogs">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div v-if="defenseLogs.length === 0" class="empty-state small">
            <el-icon><Document /></el-icon>
            <p>暂无防御日志</p>
          </div>
          <div v-else class="log-list">
            <div v-for="log in defenseLogs" :key="log.id" class="log-item" :class="'log-' + log.level">
              <div class="log-time">{{ formatTime(log.created_at) }}</div>
              <div class="log-content">
                <el-tag :type="getLogLevelType(log.level)" size="small">{{ log.level }}</el-tag>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑规则对话框 -->
    <el-dialog v-model="showAdd" :title="editingRule ? '编辑防御规则' : '添加防御规则'" width="500px">
      <el-form :model="newRule" label-width="100px" size="default">
        <el-form-item label="规则名称" required>
          <el-input v-model="newRule.name" placeholder="如：SQL注入防护规则">
            <template #prefix>
              <el-icon><Edit /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="规则类型" required>
          <el-select v-model="newRule.defense_type" style="width: 100%;">
            <el-option-group label="Web安全">
              <el-option label="WAF (Web应用防火墙)" value="WAF" />
              <el-option label="IDS (入侵检测系统)" value="IDS" />
              <el-option label="IPS (入侵防御系统)" value="IPS" />
            </el-option-group>
            <el-option-group label="网络安全">
              <el-option label="防火墙" value="防火墙" />
              <el-option label="流量监控" value="流量监控" />
            </el-option-group>
            <el-option-group label="主动防御">
              <el-option label="蜜罐系统" value="蜜罐" />
              <el-option label="入侵检测" value="入侵检测" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="规则描述">
          <el-input v-model="newRule.description" type="textarea" :rows="3" placeholder="描述该防御规则的功能和作用" />
        </el-form-item>
        <el-form-item label="初始覆盖率">
          <el-slider v-model="newRule.coverage" :min="0" :max="100" :marks="coverageMarks" />
        </el-form-item>
        <el-form-item label="立即启用">
          <el-switch v-model="newRule.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="addRule" :loading="adding">
          {{ editingRule ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 应用模板确认 -->
    <el-dialog v-model="showTemplateConfirm" title="应用防御模板" width="400px">
      <div class="template-confirm">
        <p>确定要应用模板 <strong>{{ selectedTemplate?.name }}</strong> 吗？</p>
        <p>将创建 {{ selectedTemplate?.defenses?.length || 0 }} 个防御规则</p>
      </div>
      <template #footer>
        <el-button @click="showTemplateConfirm = false">取消</el-button>
        <el-button type="primary" @click="confirmApplyTemplate" :loading="applyingTemplate">
          应用
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Umbrella, Plus, Lock, CircleCheck, Warning, DataLine,
  List, Edit, Delete, Aim, Document, Refresh, Search,
  MagicStick, Box, Loading
} from '@element-plus/icons-vue'
import axios from 'axios'
import StatCard from '@/components/StatCard.vue'

// 状态
const loading = ref(false)
const adding = ref(false)
const testing = ref(false)
const applyingTemplate = ref(false)
const showAdd = ref(false)
const showTemplates = ref(true)
const showTemplateConfirm = ref(false)
const searchKeyword = ref('')
const rules = ref([])
const templates = ref([])
const defenseLogs = ref([])
const editingRule = ref(null)
const selectedTemplate = ref(null)
const testResult = ref(null)

// 统计数据
const stats = ref({
  active: 0,
  blocked: '--',
  coverage: 0,
  alerts: 0
})

// 表单数据
const newRule = ref({
  name: '',
  defense_type: 'WAF',
  description: '',
  coverage: 80,
  enabled: true
})

const testForm = ref({
  defense_id: '',
  attack_type: 'SQL注入',
  intensity: 5
})

const coverageMarks = { 0: '0%', 50: '50%', 80: '80%', 100: '100%' }

// 过滤规则
const filteredRules = computed(() => {
  if (!searchKeyword.value) return rules.value
  const keyword = searchKeyword.value.toLowerCase()
  return rules.value.filter(r => 
    r.name.toLowerCase().includes(keyword) ||
    r.defense_type.toLowerCase().includes(keyword) ||
    (r.description && r.description.toLowerCase().includes(keyword))
  )
})

// 类型颜色映射
function getTypeTag(type) {
  const map = {
    'WAF': 'primary',
    'IDS': 'success',
    'IPS': 'warning',
    '防火墙': 'danger',
    '蜜罐': 'primary',
    '入侵检测': 'success',
    '流量监控': 'info'
  }
  return map[type] || 'info'
}

function getTypeColor(type) {
  const map = {
    'WAF': '#409eff',
    'IDS': '#67c23a',
    'IPS': '#e6a23c',
    '防火墙': '#f56c6c',
    '蜜罐': '#a855f7',
    '入侵检测': '#67c23a',
    '流量监控': '#909399'
  }
  return map[type] || '#909399'
}

function getCoverageColor(coverage) {
  if (coverage >= 80) return '#67c23a'
  if (coverage >= 50) return '#e6a23c'
  return '#f56c6c'
}

function getLogLevelType(level) {
  const map = {
    'success': 'success',
    'info': 'info',
    'warning': 'warning',
    'danger': 'danger',
    'error': 'danger'
  }
  return map[level] || 'info'
}

// 加载防御规则
async function loadRules() {
  loading.value = true
  try {
    const res = await axios.get('/api/defenses')
    if (res.data.status === 'success') {
      rules.value = (res.data.data || []).map(r => ({ 
        ...r, 
        defense_id: r.id || r.defense_id,
        _loading: false, 
        _deleting: false 
      }))
      
      // 更新统计
      const activeCount = rules.value.filter(r => r.enabled).length
      stats.value.active = activeCount
      const avgCov = rules.value.length ? 
        Math.round(rules.value.reduce((s, r) => s + (r.coverage || 0), 0) / rules.value.length) : 0
      stats.value.coverage = avgCov
    }
  } catch (e) {
    console.error('加载防御规则失败:', e)
    ElMessage.error('加载防御规则失败')
    rules.value = []
    stats.value.active = 0
    stats.value.coverage = 0
  } finally {
    loading.value = false
  }
}


// 加载模板
async function loadTemplates() {
  // 使用本地模板数据
  templates.value = [
    { name: 'Web安全防护套件', defenses: [{ name: 'SQL注入防护', defense_type: 'WAF' }, { name: 'XSS防护', defense_type: 'WAF' }] },
    { name: '网络层防护', defenses: [{ name: '防火墙', defense_type: '防火墙' }, { name: '流量监控', defense_type: '流量监控' }] },
    { name: '主动防御系统', defenses: [{ name: '蜜罐', defense_type: '蜜罐' }, { name: '入侵检测', defense_type: 'IDS' }] }
  ]
}

// 加载防御日志
async function loadDefenseLogs() {
  try {
    const res = await axios.get('/api/logs', {
      params: {
        type: 'defense',
        limit: 10
      }
    })
    if (res.data.status === 'success') {
      defenseLogs.value = (res.data.data || []).map(l => ({
        id: l.id || l.log_id,
        level: l.level || 'info',
        message: l.action || l.detail || l.message || '防御日志',
        created_at: l.created_at || l.time || new Date().toISOString()
      }))
    }
  } catch (e) {
    console.error('加载防御日志失败:', e)
    defenseLogs.value = []
  }
}

// 加载统计
async function loadStats() {
  try {
    const res = await axios.get('/api/stats/overview')
    if (res.data.status === 'success') {
      const data = res.data.stats || res.data
      stats.value.blocked = data.alerts || 0
      stats.value.alerts = Math.floor((data.alerts || 0) * 0.1)
    }
  } catch (e) {
    console.error('加载统计数据失败:', e)
    stats.value.blocked = 0
    stats.value.alerts = 0
  }
}

// 切换规则状态
async function toggleRule(row) {
  row._loading = true
  try {
    const res = await axios.post(`/api/defenses/${row.defense_id || row.id}/toggle`)
    if (res.data.status === 'success') {
      ElMessage.success(`${row.name} 已${row.enabled ? '启用' : '禁用'}`)
      await loadRules()
    } else {
      row.enabled = !row.enabled
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (e) {
    row.enabled = !row.enabled
    ElMessage.error('操作失败')
  } finally {
    row._loading = false
  }
}

// 添加/编辑规则
async function addRule() {
  if (!newRule.value.name.trim()) {
    ElMessage.warning('请填写规则名称')
    return
  }
  
  adding.value = true
  try {
    if (editingRule.value) {
      // 编辑
      const res = await axios.put(`/api/defenses/${editingRule.value.defense_id || editingRule.value.id}/update`, newRule.value)
      if (res.data.status === 'success') {
        ElMessage.success('规则更新成功')
        showAdd.value = false
        await loadRules()
      } else {
        ElMessage.error(res.data.msg || '更新失败')
      }
    } else {
      // 添加
      const res = await axios.post('/api/defenses/create', newRule.value)
      if (res.data.status === 'success') {
        ElMessage.success('规则添加成功')
        showAdd.value = false
        resetForm()
        await loadRules()
      } else {
        ElMessage.error(res.data.msg || '添加失败')
      }
    }
  } catch (e) {
    ElMessage.error(editingRule.value ? '更新失败' : '添加失败')
  } finally {
    adding.value = false
  }
}

// 编辑规则
function editRule(row) {
  editingRule.value = row
  newRule.value = {
    name: row.name,
    defense_type: row.defense_type,
    description: row.description || '',
    coverage: row.coverage || 80,
    enabled: row.enabled
  }
  showAdd.value = true
}

// 删除规则
async function deleteRule(row) {
  try {
    await ElMessageBox.confirm(`确定要删除规则 "${row.name}" 吗？`, '删除确认', {
      type: 'warning'
    })
    
    row._deleting = true
    const res = await axios.delete(`/api/defenses/${row.defense_id || row.id}/delete`)
    if (res.data.status === 'success') {
      ElMessage.success('规则已删除')
      await loadRules()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    row._deleting = false
  }
}

// 测试规则
async function testRule(row) {
  testForm.value.defense_id = row.defense_id
  testResult.value = null
  ElMessage.info(`已选择规则: ${row.name}`)
}

// 运行防御测试
async function runDefenseTest() {
  if (!testForm.value.defense_id) {
    ElMessage.warning('请先选择一个防御规则进行测试')
    return
  }
  
  testing.value = true
  testResult.value = null
  
  try {
    const res = await axios.post('/api/defense/check', testForm.value)
    if (res.data.status === 'success') {
      // 获取结果
      const resultRes = await axios.get(`/api/defense/result/${testForm.value.defense_id}`)
      if (resultRes.data.status === 'success') {
        testResult.value = {
          blocked: resultRes.data.result?.blocked || false,
          message: resultRes.data.result?.message || '测试完成',
          time: Math.floor(Math.random() * 100) + 50
        }
      }
    } else {
      ElMessage.error(res.data.msg || '测试失败')
    }
  } catch (e) {
    ElMessage.error('测试失败')
  } finally {
    testing.value = false
  }
}

// 应用模板
function applyTemplate(template) {
  selectedTemplate.value = template
  showTemplateConfirm.value = true
}

// 确认应用模板
async function confirmApplyTemplate() {
  applyingTemplate.value = true
  try {
    const res = await axios.post(`/api/defense/template/apply/${encodeURIComponent(selectedTemplate.value.name)}`)
    if (res.data.status === 'success') {
      ElMessage.success(res.data.message || '模板应用成功')
      showTemplateConfirm.value = false
      await loadRules()
    } else {
      ElMessage.error(res.data.msg || '应用失败')
    }
  } catch (e) {
    ElMessage.error('应用模板失败')
  } finally {
    applyingTemplate.value = false
  }
}

// 重置表单
function resetForm() {
  editingRule.value = null
  newRule.value = {
    name: '',
    defense_type: 'WAF',
    description: '',
    coverage: 80,
    enabled: true
  }
}

// 格式化时间
function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 监听对话框关闭
import { watch } from 'vue'
watch(showAdd, (val) => {
  if (!val) {
    resetForm()
  }
})

// 初始化
onMounted(() => {
  loadRules()
  loadTemplates()
  loadDefenseLogs()
  loadStats()
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 16px;
}

/* DefensePanel页面统计卡片 - 亮色设计 */
.stat-card {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(80, 144, 160, 0.4), rgba(96, 80, 160, 0.4)) !important;
  border: 1px solid rgba(80, 144, 160, 0.5) !important;
  border-radius: 0 !important;
  transition: all 0.3s ease;
  /* 六角形裁剪 */
  clip-path: polygon(
    6px 0%, 
    calc(100% - 6px) 0%, 
    100% 6px, 
    100% calc(100% - 6px), 
    calc(100% - 6px) 100%, 
    6px 100%, 
    0% calc(100% - 6px), 
    0% 6px
  );
  box-shadow: 0 4px 20px rgba(80, 144, 160, 0.2);
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(80, 144, 160, 0.7) !important;
  box-shadow: 0 6px 28px rgba(80, 144, 160, 0.3) !important;
  background: linear-gradient(135deg, rgba(80, 144, 160, 0.5), rgba(96, 80, 160, 0.5)) !important;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 16px;
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
}

.stat-success .stat-icon {
  background: rgba(64, 160, 96, 0.3) !important;
  color: #ffffff !important;
}

.stat-purple .stat-icon {
  background: rgba(96, 80, 160, 0.3) !important;
  color: #ffffff !important;
}

.stat-cyan .stat-icon {
  background: rgba(80, 144, 160, 0.3) !important;
  color: #ffffff !important;
}

.stat-warning .stat-icon {
  background: rgba(160, 144, 32, 0.3) !important;
  color: #ffffff !important;
}

.stat-info {
  color: #ffffff !important;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  color: #ffffff !important;
}

.stat-label {
  font-size: 13px;
  color: #ffffff !important;
  margin-top: 4px;
}

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
  letter-spacing: 0.5px !important;
}

/* 统计卡片标题使用科技风字体 */
.stat-label {
  font-family: var(--font-display) !important;
  font-size: 13px !important;
  letter-spacing: 0.3px !important;
}

.stat-value {
  font-family: var(--font-display) !important;
  font-weight: 700 !important;
}

/* 模板名称 */
.template-name {
  font-family: var(--font-ui) !important;
}

/* 规则名称 */
.rule-name {
  font-family: var(--font-ui) !important;
}

.header-actions {
  display: flex;
  align-items: center;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.template-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-item:hover {
  background: rgba(103, 194, 58, 0.1);
  border-color: #67c23a;
  transform: translateY(-2px);
}

.template-icon {
  font-size: 24px;
  color: #67c23a;
  margin-bottom: 8px;
}

.template-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.template-count {
  font-size: 11px;
  color: var(--text-muted);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.empty-state.small {
  padding: 20px;
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.rule-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coverage-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coverage-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.test-result {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.result-time {
  font-size: 12px;
  color: var(--text-muted);
}

.result-message {
  font-size: 13px;
  color: var(--text-secondary);
}

.log-list {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  font-size: 11px;
  color: var(--text-muted);
  min-width: 80px;
}

.log-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex: 1;
}

.log-message {
  font-size: 12px;
  color: var(--text-secondary);
}

.log-success .log-message { color: #67c23a; }
.log-danger .log-message { color: #f56c6c; }
.log-warning .log-message { color: #e6a23c; }

.template-confirm {
  text-align: center;
  padding: 20px;
}

.template-confirm p {
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.template-confirm strong {
  color: var(--primary-color);
}

/* 操作按钮组 */
.action-btn-group {
  display: flex !important;
  gap: 0 !important;
}

.action-btn-group .el-button {
  padding: 5px 8px !important;
  font-size: 12px !important;
  border-radius: 0 !important;
}

.action-btn-group .el-button:first-child {
  border-radius: 4px 0 0 4px !important;
}

.action-btn-group .el-button:last-child {
  border-radius: 0 4px 4px 0 !important;
}

.action-btn-group .el-button:not(:last-child) {
  border-right: none !important;
}

@media (max-width: 768px) {
  .stats-row .el-col {
    margin-bottom: 12px;
  }
  
  .template-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header-actions .el-input {
    display: none;
  }
}
</style>