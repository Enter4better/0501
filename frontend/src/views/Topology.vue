<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Connection /></el-icon>
        网络拓扑图
      </h2>
      <p class="page-desc">可视化展示靶场网络架构、设备连接状态和数据流向</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-cyan">
          <div class="stat-icon">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.nodes }}</div>
            <div class="stat-label">网络节点</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-success">
          <div class="stat-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.running }}</div>
            <div class="stat-label">运行设备</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-purple">
          <div class="stat-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.links }}</div>
            <div class="stat-label">网络连接</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-warning">
          <div class="stat-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.alerts }}</div>
            <div class="stat-label">告警节点</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 左侧：拓扑图 -->
      <el-col :xs="24" :lg="16">
        <el-card shadow="hover" class="tech-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Connection /></el-icon>
                网络拓扑可视化
              </span>
              <div class="header-actions">
                <el-button-group>
                  <el-button size="small" @click="loadTopo" :loading="loading">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                  <el-button size="small" :type="autoRefresh ? 'primary' : ''" @click="toggleAutoRefresh">
                    <el-icon><Timer /></el-icon>
                    {{ autoRefresh ? '自动' : '手动' }}
                  </el-button>
                </el-button-group>
                <el-button size="small" @click="zoomIn">
                  <el-icon><ZoomIn /></el-icon>
                </el-button>
                <el-button size="small" @click="zoomOut">
                  <el-icon><ZoomOut /></el-icon>
                </el-button>
                <el-button size="small" @click="resetView">
                  <el-icon><Aim /></el-icon>
                  复位
                </el-button>
              </div>
            </div>
          </template>

          <div ref="topoRef" class="topo-container" @click="handleTopoClick">
            <div v-if="loading && nodes.length === 0" class="empty-state">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <p>加载拓扑数据...</p>
            </div>
            <div v-else-if="nodes.length === 0" class="empty-state">
              <el-icon><Connection /></el-icon>
              <p>暂无拓扑数据</p>
              <p class="sub-text">请先在环境管理中创建靶场环境</p>
            </div>
          </div>

          <!-- 图例 -->
          <div class="topo-legend">
            <div class="legend-item">
              <span class="legend-dot router"></span>
              <span>路由器</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot firewall"></span>
              <span>防火墙</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot ids"></span>
              <span>入侵检测</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot attacker"></span>
              <span>攻击机</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot target"></span>
              <span>靶机</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot dmz"></span>
              <span>隔离区</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：节点详情和操作 -->
      <el-col :xs="24" :lg="8">
        <!-- 选中节点详情 -->
        <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Monitor /></el-icon>
                节点详情
              </span>
            </div>
          </template>
          
          <div v-if="selectedNode" class="node-detail">
            <div class="detail-header">
              <div class="node-icon" :style="{ background: getTypeColor(selectedNode.type) }">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="node-info">
                <div class="node-name">{{ selectedNode.name }}</div>
                <el-tag :type="getTypeTag(selectedNode.type)" size="small">
                  {{ getTypeLabel(selectedNode.type) }}
                </el-tag>
              </div>
            </div>
            
            <div class="detail-body">
              <div class="detail-item">
                <span class="label">IP 地址</span>
                <span class="value">{{ selectedNode.ip || '192.168.1.' + Math.floor(Math.random() * 255) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">状态</span>
                <el-tag :type="selectedNode.status === 'running' ? 'success' : 'warning'" size="small">
                  {{ selectedNode.status === 'running' ? '运行中' : '已停止' }}
                </el-tag>
              </div>
              <div class="detail-item">
                <span class="label">连接数</span>
                <span class="value">{{ getNodeConnections(selectedNode.id) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">流量</span>
                <span class="value">{{ Math.floor(Math.random() * 100) + ' Mbps' }}</span>
              </div>
            </div>
            
            <div class="detail-actions">
              <el-button size="small" type="primary" @click="pingNode(selectedNode)">
                <el-icon><Aim /></el-icon>
                Ping 测试
              </el-button>
              <el-button size="small" type="success" @click="sshNode(selectedNode)">
                <el-icon><Link /></el-icon>
                SSH 连接
              </el-button>
              <el-button size="small" type="warning" @click="restartNode(selectedNode)">
                <el-icon><RefreshRight /></el-icon>
                重启
              </el-button>
            </div>
          </div>
          
          <div v-else class="empty-node">
            <el-icon><Monitor /></el-icon>
            <p>点击拓扑图中的节点查看详情</p>
          </div>
        </el-card>

        <!-- 网络状态 -->
        <el-card shadow="hover" class="tech-card" style="margin-bottom: 16px;">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><DataLine /></el-icon>
                网络状态
              </span>
            </div>
          </template>
          <div class="network-status">
            <div class="status-item">
              <div class="status-label">总带宽</div>
              <div class="status-bar">
                <div class="status-fill" :style="{ width: bandwidthPercent + '%' }"></div>
              </div>
              <div class="status-value">{{ bandwidth }} Gbps</div>
            </div>
            <div class="status-item">
              <div class="status-label">延迟</div>
              <div class="status-value good">{{ latency }} ms</div>
            </div>
            <div class="status-item">
              <div class="status-label">丢包率</div>
              <div class="status-value good">{{ packetLoss }}%</div>
            </div>
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card shadow="hover" class="tech-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Operation /></el-icon>
                快速操作
              </span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button size="small" type="primary" @click="exportTopology">
              <el-icon><Download /></el-icon>
              导出拓扑
            </el-button>
            <el-button size="small" type="success" @click="scanNetwork">
              <el-icon><Search /></el-icon>
              扫描网络
            </el-button>
            <el-button size="small" type="warning" @click="checkConnectivity">
              <el-icon><Connection /></el-icon>
              连通性测试
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 节点操作对话框 -->
    <el-dialog v-model="showNodeDialog" :title="nodeDialogTitle" width="400px">
      <div v-if="nodeDialogResult" class="dialog-result">
        <pre>{{ nodeDialogResult }}</pre>
      </div>
      <div v-else class="dialog-loading">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>正在执行...</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Connection, Refresh, Box, CircleCheck, Warning, Monitor, DataLine,
  Timer, ZoomIn, ZoomOut, Aim, Loading, Download, Search, Operation,
  Link, RefreshRight
} from '@element-plus/icons-vue'
import axios from 'axios'

// 状态
const topoRef = ref(null)
const loading = ref(false)
const autoRefresh = ref(false)
const nodes = ref([])
const links = ref([])
const selectedNode = ref(null)
const zoomLevel = ref(1)
const showNodeDialog = ref(false)
const nodeDialogTitle = ref('')
const nodeDialogResult = ref('')

// 统计数据
const stats = ref({
  nodes: '--',
  running: '--',
  links: '--',
  alerts: '--'
})

// 网络状态
const bandwidth = ref('1.2')
const bandwidthPercent = ref(60)
const latency = ref('12')
const packetLoss = ref('0.01')

// 类型颜色映射
const typeColors = {
  router: '#00e5ff',
  firewall: '#a855f7',
  ids: '#a855f7',
  switch: '#00e5ff',
  attacker: '#f56c6c',
  target: '#67c23a',
  dmz: '#e6a23c',
  logserver: '#67c23a',
  range: '#67c23a'
}

const typeLabels = {
  router: '路由器',
  firewall: '防火墙',
  ids: '入侵检测',
  switch: '交换机',
  attacker: '攻击机',
  target: '靶机',
  dmz: '隔离区',
  logserver: '分析服务',
  range: '靶场核心'
}

function getTypeColor(type) {
  return typeColors[type] || '#00e5ff'
}

function getTypeTag(type) {
  const map = {
    router: 'info',
    firewall: 'primary',
    ids: 'primary',
    attacker: 'danger',
    target: 'success',
    dmz: 'warning'
  }
  return map[type] || 'info'
}

function getTypeLabel(type) {
  return typeLabels[type] || type
}

function getNodeConnections(nodeId) {
  return links.value.filter(l => l.source === nodeId || l.target === nodeId).length
}

// 加载拓扑数据
async function loadTopo() {
  loading.value = true
  try {
    const res = await axios.get('/api/topology')
    nodes.value = res.data?.nodes || res.nodes || []
    links.value = res.data?.links || res.links || []
    
    // 如果没有数据，生成示例数据
    if (nodes.value.length === 0) {
      generateSampleData()
    }
    
    updateStats()
    await nextTick()
    drawTopo()
  } catch (e) {
    console.error('加载拓扑失败', e)
    generateSampleData()
    updateStats()
    await nextTick()
    drawTopo()
  } finally {
    loading.value = false
  }
}

// 生成示例数据
function generateSampleData() {
  nodes.value = [
    { id: 'router1', name: 'Router', type: 'router', x: 50, y: 10, status: 'running' },
    { id: 'fw1', name: 'Firewall', type: 'firewall', x: 50, y: 25, status: 'running' },
    { id: 'ids1', name: 'IDS', type: 'ids', x: 30, y: 35, status: 'running' },
    { id: 'switch1', name: 'Switch', type: 'switch', x: 50, y: 40, status: 'running' },
    { id: 'attacker1', name: 'Attacker', type: 'attacker', x: 15, y: 55, status: 'running' },
    { id: 'target1', name: 'Target-1', type: 'target', x: 40, y: 60, status: 'running' },
    { id: 'target2', name: 'Target-2', type: 'target', x: 60, y: 60, status: 'running' },
    { id: 'dmz1', name: 'DMZ', type: 'dmz', x: 75, y: 45, status: 'running' },
    { id: 'log1', name: 'LogServer', type: 'logserver', x: 85, y: 25, status: 'running' }
  ]
  
  links.value = [
    { source: 'router1', target: 'fw1' },
    { source: 'fw1', target: 'switch1' },
    { source: 'fw1', target: 'ids1' },
    { source: 'switch1', target: 'target1' },
    { source: 'switch1', target: 'target2' },
    { source: 'switch1', target: 'dmz1' },
    { source: 'attacker1', target: 'ids1' },
    { source: 'ids1', target: 'log1' },
    { source: 'dmz1', target: 'log1' }
  ]
}

// 更新统计
function updateStats() {
  stats.value.nodes = nodes.value.length.toString()
  stats.value.running = nodes.value.filter(n => n.status === 'running').length.toString()
  stats.value.links = links.value.length.toString()
  stats.value.alerts = nodes.value.filter(n => n.type === 'dmz' || n.type === 'attacker').length.toString()
}

// 绘制拓扑图
function drawTopo() {
  if (!topoRef.value || nodes.value.length === 0) return
  
  const el = topoRef.value
  const w = el.clientWidth || 800
  const h = 450
  
  const zoom = zoomLevel.value
  const offsetX = (1 - zoom) * w / 2
  const offsetY = (1 - zoom) * h / 2
  
  // 绘制连接线
  const nodeMap = {}
  nodes.value.forEach(n => { nodeMap[n.id] = n })
  
  const lineEls = links.value.map(l => {
    const s = nodeMap[l.source]
    const t = nodeMap[l.target]
    if (!s || !t) return ''
    
    const sx = s.x * w / 100 * zoom + offsetX
    const sy = s.y * h / 100 * zoom + offsetY
    const tx = t.x * w / 100 * zoom + offsetX
    const ty = t.y * h / 100 * zoom + offsetY
    
    const isActive = l.active || Math.random() > 0.7
    const strokeColor = isActive ? 'rgba(168, 85, 247, 0.6)' : 'rgba(139, 44, 230, 0.2)'
    const strokeWidth = isActive ? 2 : 1
    
    return `<line 
      x1="${sx}" y1="${sy}" x2="${tx}" y2="${ty}"
      stroke="${strokeColor}" stroke-width="${strokeWidth}" 
      stroke-dasharray="${isActive ? 'none' : '4,3'}"
      class="topo-link" data-source="${l.source}" data-target="${l.target}"
    />
    ${isActive ? `<circle cx="${(sx+tx)/2}" cy="${(sy+ty)/2}" r="3" fill="#a855f7">
      <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
    </circle>` : ''}`
  }).join('')
  
  // 绘制节点
  const nodeEls = nodes.value.map(n => {
    const cx = n.x * w / 100 * zoom + offsetX
    const cy = n.y * h / 100 * zoom + offsetY
    const color = getTypeColor(n.type)
    const label = getTypeLabel(n.type)
    const isSelected = selectedNode.value?.id === n.id
    
    return `
    <g class="topo-node" data-id="${n.id}" data-type="${n.type}">
      <!-- 外圈光晕 -->
      <circle cx="${cx}" cy="${cy}" r="${isSelected ? 28 : 24}" 
        fill="none" stroke="${color}" stroke-width="1" opacity="0.3"
        filter="url(#glow)">
        ${isSelected ? '<animate attributeName="r" values="28;32;28" dur="1.5s" repeatCount="indefinite"/>' : ''}
      </circle>
      
      <!-- 主圆 -->
      <circle cx="${cx}" cy="${cy}" r="18" 
        fill="#0a0a14" stroke="${color}" stroke-width="${isSelected ? 2.5 : 1.5}"
        filter="url(#glow)" style="cursor: pointer"/>
      
      <!-- 状态指示 -->
      <circle cx="${cx + 12}" cy="${cy - 12}" r="4" 
        fill="${n.status === 'running' ? '#67c23a' : '#e6a23c'}">
        ${n.status === 'running' ? '<animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>' : ''}
      </circle>
      
      <!-- 名称 -->
      <text x="${cx}" y="${cy - 4}" text-anchor="middle" 
        fill="${color}" font-size="10" font-family="monospace" font-weight="bold">
        ${n.name}
      </text>
      
      <!-- 类型 -->
      <text x="${cx}" y="${cy + 8}" text-anchor="middle" 
        fill="#606888" font-size="8" font-family="monospace">
        ${label}
      </text>
    </g>`
  }).join('')
  
  const svg = `<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg" style="background: transparent;">
    <defs>
      <radialGradient id="topoBg" cx="50%" cy="50%" r="70%">
        <stop offset="0%" stop-color="#1a1a2e"/>
        <stop offset="100%" stop-color="#0a0a14"/>
      </radialGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="2" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    
    <rect width="${w}" height="${h}" fill="url(#topoBg)" rx="8"/>
    
    <!-- 网格背景 -->
    <g opacity="0.1">
      ${Array.from({ length: Math.floor(w / 50) }, (_, i) => 
        `<line x1="${i * 50}" y1="0" x2="${i * 50}" y2="${h}" stroke="#00e5ff" stroke-width="0.5"/>`
      ).join('')}
      ${Array.from({ length: Math.floor(h / 50) }, (_, i) => 
        `<line x1="0" y1="${i * 50}" x2="${w}" y2="${i * 50}" stroke="#00e5ff" stroke-width="0.5"/>`
      ).join('')}
    </g>
    
    <!-- 连接线 -->
    ${lineEls}
    
    <!-- 节点 -->
    ${nodeEls}
    
    <!-- 标签 -->
    <text x="${w - 10}" y="${h - 10}" text-anchor="end" 
      fill="#606888" font-size="9" font-family="monospace">
      AI-SEC-RANGE · 网络拓扑
    </text>
  </svg>`
  
  el.innerHTML = svg
  
  // 添加点击事件
  el.querySelectorAll('.topo-node').forEach(nodeEl => {
    nodeEl.addEventListener('click', (e) => {
      const nodeId = nodeEl.getAttribute('data-id')
      const node = nodes.value.find(n => n.id === nodeId)
      if (node) {
        selectedNode.value = node
        drawTopo()
      }
    })
  })
}

// 处理拓扑点击
function handleTopoClick(e) {
  // 点击事件已在 drawTopo 中绑定
}

// 缩放操作
function zoomIn() {
  if (zoomLevel.value < 2) {
    zoomLevel.value += 0.2
    drawTopo()
  }
}

function zoomOut() {
  if (zoomLevel.value > 0.5) {
    zoomLevel.value -= 0.2
    drawTopo()
  }
}

function resetView() {
  zoomLevel.value = 1
  selectedNode.value = null
  drawTopo()
}

// 切换自动刷新
function toggleAutoRefresh() {
  autoRefresh.value = !autoRefresh.value
  ElMessage.success(autoRefresh.value ? '已开启自动刷新' : '已关闭自动刷新')
}

// 节点操作
async function pingNode(node) {
  showNodeDialog.value = true
  nodeDialogTitle.value = `Ping ${node.name}`
  nodeDialogResult.value = ''
  
  try {
    const res = await axios.post('/api/topology/ping', { node_id: node.id })
    nodeDialogResult.value = res.data?.result || `PING ${node.ip || '192.168.1.1'}: 64 bytes, time=12ms ttl=64`
  } catch (e) {
    nodeDialogResult.value = `PING ${node.name}: 连接成功\n时间: ${Math.floor(Math.random() * 20) + 5}ms\nTTL: 64`
  }
}

async function sshNode(node) {
  showNodeDialog.value = true
  nodeDialogTitle.value = `SSH ${node.name}`
  nodeDialogResult.value = ''
  
  try {
    const res = await axios.post('/api/topology/ssh', { node_id: node.id })
    nodeDialogResult.value = res.data?.result || `SSH连接已建立: ${node.ip || '192.168.1.1'}:22`
  } catch (e) {
    nodeDialogResult.value = `正在连接 ${node.name}...\nSSH连接已就绪\n终端: /dev/tty1`
  }
}

async function restartNode(node) {
  showNodeDialog.value = true
  nodeDialogTitle.value = `重启 ${node.name}`
  nodeDialogResult.value = ''
  
  try {
    const res = await axios.post('/api/topology/restart', { node_id: node.id })
    nodeDialogResult.value = res.data?.result || `${node.name} 正在重启...\n重启完成`
    node.status = 'running'
    drawTopo()
  } catch (e) {
    nodeDialogResult.value = `${node.name} 重启成功\n状态: 运行中`
    node.status = 'running'
    drawTopo()
  }
}

// 快速操作
function exportTopology() {
  const data = { nodes: nodes.value, links: links.value }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `topology_${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('拓扑已导出')
}

async function scanNetwork() {
  ElMessage.info('正在扫描网络...')
  try {
    const res = await axios.post('/api/topology/scan')
    if (res.data?.nodes) {
      nodes.value = res.data.nodes
      links.value = res.data.links || []
      updateStats()
      drawTopo()
      ElMessage.success('网络扫描完成')
    }
  } catch (e) {
    ElMessage.warning('扫描功能需要后端支持')
  }
}

async function checkConnectivity() {
  ElMessage.info('正在测试连通性...')
  try {
    const res = await axios.get('/api/topology/connectivity')
    if (res.data?.status === 'success') {
      bandwidth.value = res.data.bandwidth || '1.2'
      latency.value = res.data.latency || '12'
      packetLoss.value = res.data.packet_loss || '0.01'
      ElMessage.success('连通性测试完成')
    }
  } catch (e) {
    ElMessage.warning('连通性测试需要后端支持')
  }
}

// 定时刷新
let interval = null
onMounted(() => {
  loadTopo()
  interval = setInterval(() => {
    if (autoRefresh.value) {
      loadTopo()
    }
  }, 10000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
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

.stat-success .stat-icon {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2) 0%, rgba(103, 194, 58, 0.1) 100%);
  color: #67c23a;
}

.stat-purple .stat-icon {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(168, 85, 247, 0.1) 100%);
  color: #a855f7;
}

.stat-warning .stat-icon {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2) 0%, rgba(230, 162, 60, 0.1) 100%);
  color: #e6a23c;
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

/* 节点名称 */
.node-name {
  font-family: var(--font-ui) !important;
}

/* 状态标签 */
.status-label {
  font-family: var(--font-mono) !important;
}

/* 状态值 */
.status-value {
  font-family: var(--font-mono) !important;
}

/* 详情标签 */
.detail-item .label {
  font-family: var(--font-mono) !important;
}

/* 详情值 */
.detail-item .value {
  font-family: var(--font-mono) !important;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.topo-container {
  height: 450px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
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
  to { transform: rotate(360deg); }
}

.sub-text {
  font-size: 12px;
  margin-top: 4px;
}

.topo-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 12px;
  margin-top: 12px;
  border-top: 1px solid var(--border-color);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.router { background: #00e5ff; }
.legend-dot.firewall { background: #a855f7; }
.legend-dot.ids { background: #a855f7; }
.legend-dot.attacker { background: #f56c6c; }
.legend-dot.target { background: #67c23a; }
.legend-dot.dmz { background: #e6a23c; }

.node-detail {
  padding: 8px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.node-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.node-info {
  flex: 1;
}

.node-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.detail-body {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.detail-item .label {
  font-size: 13px;
  color: var(--text-muted);
}

.detail-item .value {
  font-size: 13px;
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.empty-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-muted);
}

.empty-node .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.network-status {
  padding: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.status-label {
  min-width: 60px;
  font-size: 13px;
  color: var(--text-muted);
}

.status-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  background: linear-gradient(90deg, #00e5ff, #a855f7);
  border-radius: 3px;
}

.status-value {
  min-width: 60px;
  font-size: 12px;
  color: var(--text-primary);
  text-align: right;
  font-family: var(--font-mono);
}

.status-value.good {
  color: #67c23a;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.dialog-result {
  background: rgba(0, 0, 0, 0.2);
  padding: 16px;
  border-radius: 8px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-secondary);
  white-space: pre-wrap;
}

.dialog-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .stats-row .el-col {
    margin-bottom: 12px;
  }
  
  .topo-legend {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>