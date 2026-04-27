 <template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Document /></el-icon>
        日志监控中心
      </h2>
      <p class="page-desc">实时监控系统安全事件、攻击日志、防御记录和系统运行状态</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <StatCard :icon="DataLine" :value="stats.total" label="总日志数" type="cyan" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard :icon="Warning" :value="stats.danger" label="危险事件" type="danger" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard :icon="CircleCheck" :value="stats.success" label="成功事件" type="success" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard :icon="Timer" :value="stats.today" label="今日日志" type="purple" />
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 左侧：日志流 -->
      <el-col :xs="24" :lg="16">
        <el-card shadow="hover" class="tech-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Document /></el-icon>
                日志流 ({{ filteredLogs.length }} 条)
              </span>
              <div class="header-actions">
                <el-input 
                  v-model="searchKeyword" 
                  placeholder="搜索日志" 
                  clearable 
                  style="width: 150px;"
                  :prefix-icon="Search"
                  size="small"
                />
                <el-select v-model="logFilter" size="small" style="width: 100px; margin-left: 8px;">
                  <el-option label="全部来源" value="all" />
                  <el-option label="攻击" value="attack" />
                  <el-option label="防御" value="defense" />
                  <el-option label="系统" value="system" />
                  <el-option label="Docker" value="docker" />
                </el-select>
                <el-select v-model="levelFilter" size="small" style="width: 100px; margin-left: 8px;">
                  <el-option label="全部级别" value="" />
                  <el-option label="危险" value="danger" />
                  <el-option label="警告" value="warning" />
                  <el-option label="成功" value="success" />
                  <el-option label="信息" value="info" />
                </el-select>
                <el-button-group style="margin-left: 8px;">
                  <el-button size="small" @click="loadLogs" :loading="loading">
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                  <el-button size="small" :type="autoRefresh ? 'primary' : ''" @click="toggleAutoRefresh">
                    <el-icon><Timer /></el-icon>
                    {{ autoRefresh ? '自动' : '手动' }}
                  </el-button>
                </el-button-group>
                <el-button size="small" type="danger" plain @click="confirmClearLogs" style="margin-left: 8px;">
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
              </div>
            </div>
          </template>

          <div ref="logContainer" class="log-container">
            <div v-if="loading && logs.length === 0" class="empty-state">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <p>加载中...</p>
            </div>
            <div v-else-if="filteredLogs.length === 0" class="empty-state">
              <el-icon><Document /></el-icon>
              <p>{{ searchKeyword ? '未找到匹配的日志' : '暂无日志记录' }}</p>
            </div>
            <div v-else class="log-list">
              <div 
                v-for="(log, i) in filteredLogs" 
                :key="log.id || i"
                class="log-row"
                :class="'log-level-' + log.level"
                @click="showLogDetail(log)"
              >
                <div class="log-time">{{ log.time }}</div>
                <el-tag 
                  :type="getLevelType(log.level)" 
                  size="small" 
                  effect="dark"
                  class="log-level-tag"
                >
                  {{ log.levelText }}
                </el-tag>
                <el-tag 
                  :type="getSourceType(log.source)" 
                  size="small"
                  class="log-source-tag"
                >
                  {{ log.source }}
                </el-tag>
                <div class="log-msg">{{ log.msg }}</div>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div class="pagination-wrapper" v-if="filteredLogs.length > 0">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[50, 100, 200, 500]"
              :total="totalLogs"
              layout="total, sizes, prev, pager, next"
              small
              background
              @change="handlePageChange"
            />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：日志分析和操作 -->
      <el-col :xs="24" :lg="8">
        <!-- 日志分布图表 -->
        <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title"><el-icon><PieChart /></el-icon> 日志分布</span>
            </div>
          </template>
          <div class="chart-container">
            <div class="chart-item">
              <div class="chart-label">危险</div>
              <div class="chart-bar">
                <div class="chart-fill danger" :style="{ width: getPercent('danger') + '%' }"></div>
              </div>
              <div class="chart-value">{{ getPercent('danger') }}%</div>
            </div>
            <div class="chart-item">
              <div class="chart-label">警告</div>
              <div class="chart-bar">
                <div class="chart-fill warning" :style="{ width: getPercent('warning') + '%' }"></div>
              </div>
              <div class="chart-value">{{ getPercent('warning') }}%</div>
            </div>
            <div class="chart-item">
              <div class="chart-label">成功</div>
              <div class="chart-bar">
                <div class="chart-fill success" :style="{ width: getPercent('success') + '%' }"></div>
              </div>
              <div class="chart-value">{{ getPercent('success') }}%</div>
            </div>
            <div class="chart-item">
              <div class="chart-label">信息</div>
              <div class="chart-bar">
                <div class="chart-fill info" :style="{ width: getPercent('info') + '%' }"></div>
              </div>
              <div class="chart-value">{{ getPercent('info') }}%</div>
            </div>
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title"><el-icon><Operation /></el-icon> 快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" size="small" @click="exportLogs('json')">
              <el-icon><Download /></el-icon>
              导出JSON
            </el-button>
            <el-button type="success" size="small" @click="exportLogs('csv')">
              <el-icon><Download /></el-icon>
              导出CSV
            </el-button>
            <el-button size="small" @click="showSearchDialog = true">
              <el-icon><Search /></el-icon>
              高级搜索
            </el-button>
          </div>
        </el-card>

        <!-- 监控服务状态 -->
        <el-card shadow="hover" class="tech-card">
          <template #header>
            <div class="card-header">
              <span class="card-title"><el-icon><Monitor /></el-icon> 监控服务</span>
              <el-tag :type="watchdogStatus.running ? 'success' : 'info'" size="small">
                {{ watchdogStatus.running ? '运行中' : '已停止' }}
              </el-tag>
            </div>
          </template>
          <div class="watchdog-info">
            <div class="watchdog-stat">
              <span class="stat-label">检查次数</span>
              <span class="stat-value">{{ watchdogStatus.checks || 0 }}</span>
            </div>
            <div class="watchdog-stat">
              <span class="stat-label">发现问题</span>
              <span class="stat-value">{{ watchdogStatus.issues || 0 }}</span>
            </div>
            <div class="watchdog-stat">
              <span class="stat-label">最后检查</span>
              <span class="stat-value">{{ watchdogStatus.last_check || '--' }}</span>
            </div>
          </div>
          <div class="watchdog-actions">
            <el-button 
              size="small" 
              :type="watchdogStatus.running ? 'warning' : 'success'"
              @click="toggleWatchdog"
              :loading="watchdogLoading"
            >
              {{ watchdogStatus.running ? '停止监控' : '启动监控' }}
            </el-button>
            <el-button size="small" @click="clearWatchdogStats">
              清空统计
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 日志详情对话框 -->
    <el-dialog v-model="showDetail" title="日志详情" width="500px">
      <div v-if="selectedLog" class="log-detail">
        <div class="detail-item">
          <span class="detail-label">时间</span>
          <span class="detail-value">{{ selectedLog.time }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">级别</span>
          <el-tag :type="getLevelType(selectedLog.level)" size="small">{{ selectedLog.levelText }}</el-tag>
        </div>
        <div class="detail-item">
          <span class="detail-label">来源</span>
          <el-tag :type="getSourceType(selectedLog.source)" size="small">{{ selectedLog.source }}</el-tag>
        </div>
        <div class="detail-item">
          <span class="detail-label">内容</span>
          <div class="detail-content">{{ selectedLog.msg }}</div>
        </div>
        <div class="detail-item" v-if="selectedLog.raw">
          <span class="detail-label">原始数据</span>
          <pre class="detail-raw">{{ selectedLog.raw }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- 高级搜索对话框 -->
    <el-dialog v-model="showSearchDialog" title="高级搜索" width="500px">
      <el-form :model="searchForm" label-width="80px" size="small">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="搜索关键词" clearable />
        </el-form-item>
        <el-form-item label="日志级别">
          <el-select v-model="searchForm.level" clearable style="width: 100%;">
            <el-option label="全部" value="" />
            <el-option label="危险" value="danger" />
            <el-option label="警告" value="warning" />
            <el-option label="成功" value="success" />
            <el-option label="信息" value="info" />
          </el-select>
        </el-form-item>
        <el-form-item label="日志来源">
          <el-select v-model="searchForm.source" clearable style="width: 100%;">
            <el-option label="全部" value="" />
            <el-option label="攻击" value="attack" />
            <el-option label="防御" value="defense" />
            <el-option label="系统" value="system" />
            <el-option label="Docker" value="docker" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker v-model="searchForm.start_date" type="datetime" placeholder="选择开始时间" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker v-model="searchForm.end_date" type="datetime" placeholder="选择结束时间" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSearchDialog = false">取消</el-button>
        <el-button type="primary" @click="performSearch" :loading="searching">搜索</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, Refresh, Delete, Warning, CircleCheck, Timer, DataLine,
  Search, Download, Operation, Monitor, PieChart, Loading
} from '@element-plus/icons-vue'
import axios from 'axios'
import StatCard from '@/components/StatCard.vue'

// 状态
const loading = ref(false)
const searching = ref(false)
const watchdogLoading = ref(false)
const logs = ref([])
const logFilter = ref('all')
const levelFilter = ref('')
const searchKeyword = ref('')
const logContainer = ref(null)
const autoRefresh = ref(true)
const showDetail = ref(false)
const showSearchDialog = ref(false)
const selectedLog = ref(null)
const currentPage = ref(1)
const pageSize = ref(100)
const totalLogs = ref(0)

// 统计数据
const stats = ref({
  total: 0,
  danger: 0,
  success: 0,
  today: 0
})

// 监控服务状态
const watchdogStatus = ref({
  running: false,
  checks: 0,
  issues: 0,
  last_check: '--'
})

// 搜索表单
const searchForm = ref({
  keyword: '',
  level: '',
  source: '',
  start_date: null,
  end_date: null
})

// 级别映射
const levelMap = { 
  danger: '危险', 
  warning: '警告', 
  success: '成功', 
  info: '信息' 
}

// 过滤日志
const filteredLogs = computed(() => {
  let result = logs.value
  
  // 来源过滤
  if (logFilter.value !== 'all') {
    result = result.filter(l => l.source === logFilter.value)
  }
  
  // 级别过滤
  if (levelFilter.value) {
    result = result.filter(l => l.level === levelFilter.value)
  }
  
  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(l => 
      l.msg.toLowerCase().includes(keyword) ||
      l.source.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

// 获取级别类型
function getLevelType(level) {
  const map = {
    'danger': 'danger',
    'warning': 'warning',
    'success': 'success',
    'info': 'info'
  }
  return map[level] || 'info'
}

// 获取来源类型
function getSourceType(source) {
  const map = {
    'attack': 'danger',
    'defense': 'success',
    'system': 'info',
    'docker': 'warning'
  }
  return map[source] || 'info'
}

// 获取百分比
function getPercent(level) {
  if (stats.value.total === 0) return 0
  const count = logs.value.filter(l => l.level === level).length
  return Math.round(count / stats.value.total * 100)
}

// 更新统计
function updateStats() {
  stats.value.total = logs.value.length
  stats.value.danger = logs.value.filter(l => l.level === 'danger').length
  stats.value.success = logs.value.filter(l => l.level === 'success').length
  stats.value.today = logs.value.filter(l => l.isToday).length
}

// 加载日志
async function loadLogs() {
  loading.value = true
  try {
    const res = await axios.get('/api/logs', {
      params: {
        page: currentPage.value,
        size: pageSize.value,
        type: logFilter.value !== 'all' ? logFilter.value : ''
      }
    })
    
    if (res.data.status === 'success') {
      const raw = res.data.data || []
      totalLogs.value = res.data.total || raw.length
      
      logs.value = raw.map(l => {
        const time = l.time || new Date().toISOString()
        return {
          id: l.id || Date.now() + Math.random(),
          time: formatTime(time),
          level: l.level || 'info',
          levelText: levelMap[l.level] || l.level || '信息',
          source: l.type || l.source || 'system',
          msg: l.action || l.detail || l.message || '系统日志',
          isToday: isToday(time),
          raw: l
        }
      })
    }
  } catch (e) {
    console.error('加载日志失败', e)
    ElMessage.error('加载日志失败')
    logs.value = []
    totalLogs.value = 0
  } finally {
    loading.value = false
  }
  
  updateStats()
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = 0
  }
}


// 格式化时间
function formatTime(time) {
  if (!time) return '--'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 判断是否今天
function isToday(time) {
  if (!time) return false
  const date = new Date(time)
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

// 切换自动刷新
function toggleAutoRefresh() {
  autoRefresh.value = !autoRefresh.value
  ElMessage.success(autoRefresh.value ? '已开启自动刷新' : '已关闭自动刷新')
}

// 显示日志详情
function showLogDetail(log) {
  selectedLog.value = log
  showDetail.value = true
}

// 确认清空日志
async function confirmClearLogs() {
  try {
    await ElMessageBox.confirm('确定要清空所有日志吗？此操作不可恢复。', '清空日志', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    await axios.post('/api/logs/clear')
    ElMessage.success('日志已清空')
    logs.value = []
    updateStats()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('清空日志失败')
    }
  }
}

// 导出日志
async function exportLogs(format) {
  try {
    const res = await axios.get('/api/logs/export', {
      params: {
        format: format,
        level: levelFilter.value,
        source: logFilter.value !== 'all' ? logFilter.value : ''
      }
    })
    
    if (format === 'csv') {
      // CSV直接下载
      const blob = new Blob([res.data], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `logs_export_${new Date().toISOString().slice(0,10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } else {
      // JSON下载
      const blob = new Blob([JSON.stringify(res.data.logs, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `logs_export_${new Date().toISOString().slice(0,10)}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
    
    ElMessage.success('日志导出成功')
  } catch (e) {
    ElMessage.error('导出日志失败')
  }
}

// 高级搜索
async function performSearch() {
  searching.value = true
  try {
    const params = {
      keyword: searchForm.value.keyword,
      level: searchForm.value.level,
      source: searchForm.value.source,
      start_date: searchForm.value.start_date?.toISOString(),
      end_date: searchForm.value.end_date?.toISOString(),
      limit: 100
    }
    
    const res = await axios.get('/api/logs/search', { params })
    
    if (res.data.status === 'success') {
      const raw = res.data.logs || []
      logs.value = raw.map(l => {
        const time = l.created_at || l.time || new Date().toISOString()
        return {
          id: l.id || Date.now() + Math.random(),
          time: formatTime(time),
          level: l.level || 'info',
          levelText: levelMap[l.level] || l.level || '信息',
          source: l.source || 'system',
          msg: l.message || l.msg || JSON.stringify(l),
          isToday: isToday(time),
          raw: l
        }
      })
      showSearchDialog.value = false
      ElMessage.success(`找到 ${logs.value.length} 条日志`)
    }
  } catch (e) {
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
  }
  
  updateStats()
}

// 加载监控状态
async function loadWatchdogStatus() {
  try {
    const res = await axios.get('/api/logs/watchdog/status')
    if (res.data.status === 'success') {
      watchdogStatus.value = res.data.watchdog || {}
    }
  } catch (e) {
    console.error('加载监控状态失败', e)
  }
}

// 切换监控服务
async function toggleWatchdog() {
  watchdogLoading.value = true
  try {
    const action = watchdogStatus.value.running ? 'stop' : 'start'
    const res = await axios.post(`/api/logs/watchdog/${action}`)
    if (res.data.status === 'success') {
      watchdogStatus.value.running = !watchdogStatus.value.running
      ElMessage.success(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    watchdogLoading.value = false
  }
}

// 清空监控统计
async function clearWatchdogStats() {
  try {
    await axios.post('/api/logs/watchdog/clear')
    watchdogStatus.value.checks = 0
    watchdogStatus.value.issues = 0
    ElMessage.success('统计已清空')
  } catch (e) {
    ElMessage.error('清空失败')
  }
}

// 分页变化
function handlePageChange() {
  loadLogs()
}

// 定时刷新
let interval = null
onMounted(() => {
  loadLogs()
  loadWatchdogStatus()
  interval = setInterval(() => {
    if (autoRefresh.value) {
      loadLogs()
      loadWatchdogStatus()
    }
  }, 5000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 16px;
}

/* Logs页面统计卡片 - 使用亮色设计 */
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

.stat-cyan .stat-icon {
  background: rgba(80, 144, 160, 0.3) !important;
  color: #ffffff !important;
}

.stat-danger .stat-icon {
  background: rgba(160, 64, 80, 0.3) !important;
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

.stat-info {
  color: #ffffff !important;
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

/* 监控统计标签 */
.watchdog-stat .stat-label {
  font-family: var(--font-display) !important;
  font-size: 11px !important;
  letter-spacing: 0.3px !important;
}

.watchdog-stat .stat-value {
  font-family: var(--font-display) !important;
  font-weight: 600 !important;
}

/* 日志时间 */
.log-time {
  font-family: var(--font-mono) !important;
}

/* 详情标签 */
.detail-label {
  font-family: var(--font-mono) !important;
}

/* 详情值 */
.detail-value {
  font-family: var(--font-ui) !important;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.log-container {
  max-height: 500px;
  overflow-y: auto;
  background: rgba(8, 10, 20, 0.55);
  border-radius: 8px;
  padding: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-muted);
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

.log-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.log-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-mono);
  font-size: 12px;
}

.log-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.log-level-danger { border-left: 3px solid #f56c6c; }
.log-level-warning { border-left: 3px solid #e6a23c; }
.log-level-success { border-left: 3px solid #67c23a; }
.log-level-info { border-left: 3px solid #909399; }

.log-time {
  color: var(--text-muted);
  white-space: nowrap;
  min-width: 100px;
}

.log-level-tag {
  min-width: 50px;
  text-align: center;
}

.log-source-tag {
  min-width: 60px;
  text-align: center;
}

.log-msg {
  color: var(--text-secondary);
  flex: 1;
  word-break: break-all;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 12px 0;
  margin-top: 12px;
  border-top: 1px solid var(--border-color);
}

.chart-container {
  padding: 8px 0;
}

.chart-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.chart-label {
  min-width: 50px;
  font-size: 13px;
  color: var(--text-secondary);
}

.chart-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.chart-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.chart-fill.danger { background: #f56c6c; }
.chart-fill.warning { background: #e6a23c; }
.chart-fill.success { background: #67c23a; }
.chart-fill.info { background: #909399; }

.chart-value {
  min-width: 40px;
  font-size: 12px;
  color: var(--text-muted);
  text-align: right;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.watchdog-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.watchdog-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}

.watchdog-stat .stat-label {
  font-size: 11px;
  color: var(--text-muted);
}

.watchdog-stat .stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.watchdog-actions {
  display: flex;
  gap: 8px;
}

.log-detail {
  padding: 8px 0;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-label {
  min-width: 60px;
  font-size: 13px;
  color: var(--text-muted);
}

.detail-value {
  font-size: 13px;
  color: var(--text-primary);
}

.detail-content {
  font-size: 13px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 6px;
  word-break: break-all;
}

.detail-raw {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  background: rgba(0, 0, 0, 0.2);
  padding: 8px 12px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 768px) {
  .stats-row .el-col {
    margin-bottom: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .header-actions .el-input {
    display: none;
  }
  
  .watchdog-info {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>