<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Cpu /></el-icon>
        AI 决策中心
      </h2>
      <p class="page-desc">基于智谱 GLM-4 大模型的安全态势智能分析与决策建议</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-cyan">
          <div class="stat-icon">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.score }}</div>
            <div class="stat-label">安全评分</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-danger">
          <div class="stat-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.threats }}</div>
            <div class="stat-label">发现威胁</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-success">
          <div class="stat-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.defenses }}</div>
            <div class="stat-label">防御规则</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-purple">
          <div class="stat-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.time }}</div>
            <div class="stat-label">分析耗时</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 左侧：AI分析报告 -->
      <el-col :xs="24" :lg="16">
        <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Cpu /></el-icon>
                AI 安全分析报告
              </span>
              <div class="header-actions">
                <span v-if="lastModel" class="model-info">
                  模型: {{ lastModel }} | 耗时: {{ lastElapsed }}s
                </span>
                <el-button type="primary" size="small" @click="generate" :loading="loading">
                  <el-icon><MagicStick /></el-icon>
                  生成报告
                </el-button>
                <el-button size="small" @click="showHistory = true">
                  <el-icon><Timer /></el-icon>
                  历史
                </el-button>
              </div>
            </div>
          </template>

          <!-- 加载状态 -->
          <div v-if="loading" class="loading-state">
            <div class="loading-animation">
              <el-icon :size="48" class="loading-icon"><Cpu /></el-icon>
              <div class="loading-pulse"></div>
            </div>
            <p class="loading-text">AI 正在分析安全态势...</p>
            <p class="loading-subtext">正在调用智谱 GLM-4 大模型进行深度分析</p>
          </div>

          <!-- 分析结果 -->
          <div v-else-if="summary" class="ai-content">
            <div class="report-header">
              <el-tag type="success" effect="dark" size="small">
                <el-icon><CircleCheck /></el-icon>
                分析完成
              </el-tag>
              <span class="report-time">{{ reportTime }}</span>
            </div>
            <div class="report-body" v-html="formattedSummary"></div>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <div class="empty-icon">
              <el-icon :size="64"><Cpu /></el-icon>
              <div class="empty-glow"></div>
            </div>
            <p class="empty-title">AI 安全态势分析</p>
            <p class="empty-desc">点击「生成报告」，AI 将基于当前靶场环境进行深度安全分析</p>
            <div class="empty-features">
              <div class="feature-item">
                <el-icon><Warning /></el-icon>
                <span>威胁识别与分析</span>
              </div>
              <div class="feature-item">
                <el-icon><Umbrella /></el-icon>
                <span>防御策略建议</span>
              </div>
              <div class="feature-item">
                <el-icon><DataLine /></el-icon>
                <span>安全评分计算</span>
              </div>
            </div>
            <p class="empty-tip">
              <el-icon><InfoFilled /></el-icon>
              点击「生成报告」开始AI安全分析
            </p>
          </div>
        </el-card>

        <!-- AI决策执行 -->
        <el-card shadow="hover" class="tech-card" v-if="summary">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Operation /></el-icon>
                AI 决策执行
              </span>
              <el-tag type="warning" size="small">自动执行需谨慎</el-tag>
            </div>
          </template>
          <div class="decision-actions">
            <el-button type="success" size="small" @click="applyDefenseRecommendations" :loading="applying">
              <el-icon><Umbrella /></el-icon>
              应用防御建议
            </el-button>
            <el-button type="danger" size="small" @click="blockThreats" :loading="blocking">
              <el-icon><Lock /></el-icon>
              阻断威胁源
            </el-button>
            <el-button size="small" @click="generateReportPDF">
              <el-icon><Download /></el-icon>
              导出报告
            </el-button>
            <el-button size="small" @click="shareReport">
              <el-icon><Share /></el-icon>
              分享报告
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：建议和威胁 -->
      <el-col :xs="24" :lg="8">
        <!-- 安全建议 -->
        <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Warning /></el-icon>
                安全建议
              </span>
              <el-badge :value="recommendations.length" type="warning" :hidden="recommendations.length === 0" />
            </div>
          </template>
          
          <div v-if="loading" class="suggestion-loading">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <p>分析中...</p>
          </div>
          
          <div v-else-if="recommendations.length > 0" class="recommendations-list">
            <el-timeline>
              <el-timeline-item 
                v-for="rec in recommendations" 
                :key="rec.id"
                :type="getUrgencyType(rec.urgency)"
                :hollow="rec.urgency !== 'high'"
                :timestamp="rec.time"
                placement="top"
              >
                <div class="recommendation-item">
                  <p class="rec-text">{{ rec.text }}</p>
                  <div class="rec-meta">
                    <el-tag 
                      :type="getUrgencyType(rec.urgency)" 
                      size="small"
                      effect="dark"
                    >
                      {{ getUrgencyText(rec.urgency) }}
                    </el-tag>
                    <el-button 
                      v-if="rec.action" 
                      text 
                      type="primary" 
                      size="small"
                      @click="executeRecommendation(rec)"
                    >
                      执行
                    </el-button>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
          
          <div v-else class="empty-suggestions">
            <el-icon><Document /></el-icon>
            <p>暂无建议</p>
            <p class="sub-text">请先生成分析报告</p>
          </div>
        </el-card>

        <!-- 威胁列表 -->
        <el-card shadow="hover" class="tech-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Aim /></el-icon>
                识别威胁
              </span>
              <el-badge :value="threats.length" type="danger" :hidden="threats.length === 0" />
            </div>
          </template>
          
          <div v-if="threats.length > 0" class="threats-list">
            <div v-for="threat in threats" :key="threat.id" class="threat-item" :class="'threat-' + threat.level">
              <div class="threat-header">
                <el-icon class="threat-icon"><Warning /></el-icon>
                <span class="threat-name">{{ threat.name }}</span>
                <el-tag :type="getThreatType(threat.level)" size="small">{{ threat.level }}</el-tag>
              </div>
              <p class="threat-desc">{{ threat.description }}</p>
              <div class="threat-actions">
                <el-button text type="danger" size="small" @click="blockThreat(threat)">
                  <el-icon><Lock /></el-icon>
                  阻断
                </el-button>
                <el-button text type="primary" size="small" @click="analyzeThreat(threat)">
                  <el-icon><Search /></el-icon>
                  分析
                </el-button>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-threats">
            <el-icon><CircleCheck /></el-icon>
            <p>未发现威胁</p>
            <p class="sub-text">系统安全状态良好</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 历史记录对话框 -->
    <el-dialog v-model="showHistory" title="AI 分析历史" width="600px">
      <div v-if="history.length === 0" class="empty-history">
        <el-icon><Timer /></el-icon>
        <p>暂无历史记录</p>
      </div>
      <el-timeline v-else>
        <el-timeline-item 
          v-for="item in history" 
          :key="item.id"
          :timestamp="item.time"
          placement="top"
        >
          <el-card shadow="hover" style="cursor: pointer;" @click="loadHistoryItem(item)">
            <div class="history-item">
              <span class="history-model">{{ item.model }}</span>
              <el-tag size="small">{{ item.score || '--' }}分</el-tag>
            </div>
            <p class="history-summary">{{ item.summary?.slice(0, 100) }}...</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>

    <!-- 威胁分析对话框 -->
    <el-dialog v-model="showThreatAnalysis" title="威胁详细分析" width="500px">
      <div v-if="selectedThreat" class="threat-analysis">
        <div class="analysis-item">
          <span class="label">威胁名称</span>
          <span class="value">{{ selectedThreat.name }}</span>
        </div>
        <div class="analysis-item">
          <span class="label">威胁等级</span>
          <el-tag :type="getThreatType(selectedThreat.level)">{{ selectedThreat.level }}</el-tag>
        </div>
        <div class="analysis-item">
          <span class="label">威胁描述</span>
          <p class="desc">{{ selectedThreat.description }}</p>
        </div>
        <div class="analysis-item">
          <span class="label">影响范围</span>
          <span class="value">{{ selectedThreat.scope || '未知' }}</span>
        </div>
        <div class="analysis-item">
          <span class="label">建议措施</span>
          <p class="desc">{{ selectedThreat.solution || '请参考AI分析报告' }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Cpu, Warning, MagicStick, Lock, DataLine, Timer, CircleCheck, Loading,
  Operation, Umbrella, Download, Share, Aim, Search, Document, InfoFilled
} from '@element-plus/icons-vue'
import axios from 'axios'

// 状态
const loading = ref(false)
const applying = ref(false)
const blocking = ref(false)
const summary = ref('')
const lastModel = ref('')
const lastElapsed = ref('')
const reportTime = ref('')
const showHistory = ref(false)
const showThreatAnalysis = ref(false)
const selectedThreat = ref(null)
const recommendations = ref([])
const threats = ref([])
const history = ref([])

// 统计数据
const stats = ref({
  score: '--',
  threats: '--',
  defenses: '--',
  time: '--'
})

// 格式化报告内容
const formattedSummary = computed(() => {
  if (!summary.value) return ''
  return summary.value
    .replace(/^### (.+)$/gm, '<h3 class="report-h3">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="report-h2">$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="report-strong">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em class="report-em">$1</em>')
    .replace(/^- (.+)$/gm, '<li class="report-li">$1</li>')
    .replace(/^\d+\. (.+)$/gm, '<li class="report-li-num">$1</li>')
    .replace(/\n\n/g, '</p><p class="report-p">')
    .replace(/\n/g, '<br/>')
})

// 获取紧急程度类型
function getUrgencyType(urgency) {
  const map = { 'high': 'danger', 'medium': 'warning', 'low': 'primary' }
  return map[urgency] || 'info'
}

// 获取紧急程度文本
function getUrgencyText(urgency) {
  const map = { 'high': '紧急', 'medium': '重要', 'low': '一般' }
  return map[urgency] || '一般'
}

// 获取威胁类型
function getThreatType(level) {
  const map = { '高危': 'danger', '中危': 'warning', '低危': 'info' }
  return map[level] || 'info'
}

// 加载统计数据
async function loadStats() {
  try {
    const [statsRes, rulesRes] = await Promise.all([
      axios.get('/api/stats'),
      axios.get('/api/defense/list'),
    ])
    
    const health = statsRes.data?.health || 0
    stats.value.score = health + '/100'
    stats.value.threats = (statsRes.data?.alerts || 0).toString()
    stats.value.defenses = ((rulesRes.data?.defenses || []).filter(r => r.enabled).length) + ' 条'
  } catch (e) {
    console.error('加载统计失败:', e)
  }
}

// 生成AI报告
async function generate() {
  loading.value = true
  summary.value = ''
  recommendations.value = []
  threats.value = []
  
  try {
    const res = await axios.post('/api/ai/summary', {})
    
    summary.value = res.data?.summary || res.summary || ''
    lastModel.value = res.data?.model || res.model || 'GLM-4'
    lastElapsed.value = res.data?.elapsed || res.elapsed || '0'
    stats.value.time = lastElapsed.value + 's'
    reportTime.value = new Date().toLocaleString('zh-CN')
    
    // 提取建议和威胁
    recommendations.value = _extractRecommendations(summary.value)
    threats.value = _extractThreats(summary.value)
    
    // 更新评分
    if (res.data?.score) {
      stats.value.score = res.data.score + '/100'
    }
    
    ElMessage.success('AI 分析完成')
    await loadStats()
    
    // 保存到历史
    history.value.unshift({
      id: Date.now(),
      time: reportTime.value,
      model: lastModel.value,
      score: res.data?.score,
      summary: summary.value
    })
    
  } catch (e) {
    const errMsg = e.response?.data?.msg || e.message
    summary.value = `<div class="error-content">
      <p>分析失败：${errMsg}</p>
      <p class="error-tip">请确保后端服务已启动</p>
      <code>cd backend && python app.py</code>
    </div>`
    ElMessage.error('AI 分析失败')
  } finally {
    loading.value = false
  }
}

// 提取建议
function _extractRecommendations(text) {
  const recs = []
  const lines = text.split('\n')
  const urgencyKeywords = { '紧急': 'high', '高': 'high', '重要': 'medium', '中': 'medium', '一般': 'low', '低': 'low' }
  const recPatterns = ['建议', '优化', '修复', '开启', '关闭', '配置', '检查', '启用', '增加', '减少', '部署', '更新']
  
  lines.forEach((line, i) => {
    const clean = line.replace(/^[-*#\s]+/, '').trim()
    if (recPatterns.some(p => clean.includes(p)) && clean.length > 5 && clean.length < 120) {
      let urgency = 'low'
      for (const [key, value] of Object.entries(urgencyKeywords)) {
        if (clean.includes(key)) {
          urgency = value
          break
        }
      }
      recs.push({
        id: i,
        text: clean,
        time: '刚刚',
        urgency: urgency,
        action: clean.includes('开启') || clean.includes('启用') || clean.includes('配置')
      })
    }
  })
  
  return recs.slice(0, 8)
}

// 提取威胁
function _extractThreats(text) {
  const threatList = []
  const lines = text.split('\n')
  const threatKeywords = ['SQL注入', 'XSS', 'CSRF', '漏洞', '攻击', '威胁', '风险', '暴露', '未授权', '弱密码', '端口', '入侵']
  const levelKeywords = { '高危': '高危', '严重': '高危', '中危': '中危', '中等': '中危', '低危': '低危', '轻微': '低危' }
  
  lines.forEach((line, i) => {
    const clean = line.replace(/^[-*#\s]+/, '').trim()
    if (threatKeywords.some(p => clean.includes(p)) && clean.length > 5) {
      let level = '中危'
      for (const [key, value] of Object.entries(levelKeywords)) {
        if (clean.includes(key)) {
          level = value
          break
        }
      }
      threatList.push({
        id: i,
        name: clean.slice(0, 30),
        description: clean,
        level: level,
        scope: '靶场环境',
        solution: '请参考AI分析报告中的建议'
      })
    }
  })
  
  return threatList.slice(0, 6)
}

// 应用防御建议
async function applyDefenseRecommendations() {
  try {
    await ElMessageBox.confirm('确定要应用AI推荐的防御策略吗？', '应用防御建议', {
      type: 'warning'
    })
    
    applying.value = true
    const res = await axios.post('/api/ai/apply-defense')
    if (res.data.status === 'success') {
      ElMessage.success('防御策略已应用')
      await loadStats()
    } else {
      ElMessage.error(res.data.msg || '应用失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('应用防御建议失败')
    }
  } finally {
    applying.value = false
  }
}

// 阻断威胁源
async function blockThreats() {
  try {
    await ElMessageBox.confirm('确定要阻断所有识别到的威胁源吗？', '阻断威胁', {
      type: 'warning'
    })
    
    blocking.value = true
    const res = await axios.post('/api/ai/block-threats')
    if (res.data.status === 'success') {
      ElMessage.success('威胁源已阻断')
      threats.value = []
    } else {
      ElMessage.error(res.data.msg || '阻断失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('阻断威胁失败')
    }
  } finally {
    blocking.value = false
  }
}

// 阻断单个威胁
async function blockThreat(threat) {
  try {
    await ElMessageBox.confirm(`确定要阻断威胁 "${threat.name}" 吗？`, '阻断威胁', {
      type: 'warning'
    })
    
    const res = await axios.post('/api/ai/block-threat', { threat_id: threat.id })
    if (res.data.status === 'success') {
      ElMessage.success('威胁已阻断')
      threats.value = threats.value.filter(t => t.id !== threat.id)
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('阻断失败')
    }
  }
}

// 分析威胁
function analyzeThreat(threat) {
  selectedThreat.value = threat
  showThreatAnalysis.value = true
}

// 执行建议
async function executeRecommendation(rec) {
  ElMessage.info(`正在执行: ${rec.text}`)
}

// 导出报告
function generateReportPDF() {
  if (!summary.value) {
    ElMessage.warning('请先生成分析报告')
    return
  }
  
  const blob = new Blob([summary.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `AI_Security_Report_${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('报告已导出')
}

// 分享报告
function shareReport() {
  ElMessage.info('分享功能开发中')
}

// 加载历史记录
function loadHistoryItem(item) {
  summary.value = item.summary
  lastModel.value = item.model
  reportTime.value = item.time
  recommendations.value = _extractRecommendations(item.summary)
  threats.value = _extractThreats(item.summary)
  showHistory.value = false
  ElMessage.success('已加载历史报告')
}

// 初始化
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, var(--card-bg) 0%, rgba(255,255,255,0.05) 100%);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 16px;
}

.stat-cyan .stat-icon {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.2) 0%, rgba(0, 229, 255, 0.1) 100%);
  color: #00e5ff;
}

.stat-danger .stat-icon {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.2) 0%, rgba(245, 108, 108, 0.1) 100%);
  color: #f56c6c;
}

.stat-success .stat-icon {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2) 0%, rgba(103, 194, 58, 0.1) 100%);
  color: #67c23a;
}

.stat-purple .stat-icon {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(168, 85, 247, 0.1) 100%);
  color: #a855f7;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
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

/* 建议文本 */
.rec-text {
  font-family: var(--font-ui) !important;
}

/* 威胁名称 */
.threat-name {
  font-family: var(--font-ui) !important;
}

/* 分析标签 */
.analysis-item .label {
  font-family: var(--font-mono) !important;
}

/* 分析值 */
.analysis-item .value {
  font-family: var(--font-ui) !important;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-info {
  font-size: 11px;
  color: var(--text-muted);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-animation {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
}

.loading-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #a855f7;
  animation: pulse 2s ease-in-out infinite;
}

.loading-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  border: 2px solid rgba(168, 85, 247, 0.3);
  border-radius: 50%;
  animation: expand 2s ease-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.5; transform: translate(-50%, -50%) scale(0.8); }
}

@keyframes expand {
  0% { width: 60px; height: 60px; opacity: 1; }
  100% { width: 100px; height: 100px; opacity: 0; }
}

.loading-text {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.loading-subtext {
  font-size: 13px;
  color: var(--text-muted);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-icon {
  position: relative;
  margin-bottom: 20px;
}

.empty-icon .el-icon {
  color: rgba(168, 85, 247, 0.5);
}

.empty-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.2) 0%, transparent 70%);
  border-radius: 50%;
}

.empty-title {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.empty-features {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.empty-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.empty-tip code {
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
}

.ai-content {
  padding: 16px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.report-time {
  font-size: 12px;
  color: var(--text-muted);
}

.report-body {
  line-height: 1.8;
}

.report-h2 {
  color: var(--text-primary);
  font-size: 18px;
  margin: 16px 0 8px;
  font-family: var(--font-display);
}

.report-h3 {
  color: #00e5ff;
  font-size: 15px;
  margin: 14px 0 6px;
  font-family: var(--font-display);
}

.report-strong {
  color: #a855f7;
  font-weight: 600;
}

.report-em {
  color: #00e5ff;
  font-style: normal;
}

.report-li, .report-li-num {
  color: var(--text-secondary);
  margin: 4px 0 4px 16px;
  font-size: 13px;
  line-height: 1.6;
  list-style: disc;
}

.report-p {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.7;
  margin: 8px 0;
}

.error-content {
  text-align: center;
  padding: 40px;
  color: #f56c6c;
}

.error-tip {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
}

.decision-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.suggestion-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: var(--text-muted);
}

.suggestion-loading .loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.recommendations-list {
  max-height: 400px;
  overflow-y: auto;
}

.recommendation-item {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 12px;
}

.rec-text {
  color: var(--text-primary);
  font-size: 13px;
  margin-bottom: 8px;
}

.rec-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-suggestions, .empty-threats {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: var(--text-muted);
}

.empty-suggestions .el-icon, .empty-threats .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.sub-text {
  font-size: 12px;
  margin-top: 4px;
}

.threats-list {
  max-height: 400px;
  overflow-y: auto;
}

.threat-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  margin-bottom: 8px;
  border-left: 3px solid;
}

.threat-high { border-left-color: #f56c6c; }
.threat-medium { border-left-color: #e6a23c; }
.threat-low { border-left-color: #909399; }

.threat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.threat-icon {
  color: #f56c6c;
}

.threat-name {
  font-size: 13px;
  color: var(--text-primary);
  flex: 1;
}

.threat-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.threat-actions {
  display: flex;
  gap: 8px;
}

.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: var(--text-muted);
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-model {
  font-size: 12px;
  color: var(--text-muted);
}

.history-summary {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.threat-analysis {
  padding: 8px 0;
}

.analysis-item {
  margin-bottom: 16px;
}

.analysis-item .label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.analysis-item .value {
  font-size: 14px;
  color: var(--text-primary);
}

.analysis-item .desc {
  font-size: 13px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 6px;
}

@media (max-width: 768px) {
  .stats-row .el-col {
    margin-bottom: 12px;
  }
  
  .empty-features {
    flex-direction: column;
  }
  
  .decision-actions {
    flex-direction: column;
  }
}
</style>