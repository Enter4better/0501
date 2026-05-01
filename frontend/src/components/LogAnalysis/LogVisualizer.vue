<template>
  <div class="log-visualizer">
    <div class="log-controls">
      <div class="filter-section">
        <label>日志级别:</label>
        <select v-model="selectedLogLevel" class="log-level-select">
          <option value="">全部</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>
      </div>
      
      <div class="filter-section">
        <label>时间范围:</label>
        <select v-model="timeRange" class="time-range-select">
          <option value="1h">1小时</option>
          <option value="6h">6小时</option>
          <option value="24h">24小时</option>
          <option value="7d">7天</option>
        </select>
      </div>
      
      <div class="filter-section">
        <label>搜索:</label>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="搜索日志..."
          class="search-input"
        />
      </div>
    </div>
    
    <div class="log-stats">
      <div class="stat-card">
        <h4>总日志数</h4>
        <div class="stat-number">{{ totalLogs }}</div>
      </div>
      <div class="stat-card">
        <h4>错误日志</h4>
        <div class="stat-number error-count">{{ errorLogs }}</div>
      </div>
      <div class="stat-card">
        <h4>警告日志</h4>
        <div class="stat-number warning-count">{{ warningLogs }}</div>
      </div>
      <div class="stat-card">
        <h4>最新日志</h4>
        <div class="stat-number">{{ latestLogTime }}</div>
      </div>
    </div>
    
    <div class="log-chart">
      <h4>日志趋势</h4>
      <div class="chart-container">
        <!-- 这里可以集成图表库如 Chart.js -->
        <div class="placeholder-chart">
          <p>日志趋势图表</p>
        </div>
      </div>
    </div>
    
    <div class="log-table-container">
      <table class="log-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>级别</th>
            <th>消息</th>
            <th>来源</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="log in filteredLogs" 
            :key="log.id" 
            :class="getRowClass(log.level)"
          >
            <td>{{ log.timestamp }}</td>
            <td>
              <span class="log-level" :class="log.level.toLowerCase()">{{ log.level }}</span>
            </td>
            <td class="log-message">{{ log.message }}</td>
            <td>{{ log.source }}</td>
            <td>
              <button @click="viewLogDetails(log)" class="btn btn-small btn-outline">
                查看
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LogVisualizer',
  props: {
    logs: Array
  },
  emits: ['view-log-details'],
  data() {
    return {
      selectedLogLevel: '',
      timeRange: '24h',
      searchQuery: ''
    }
  },
  computed: {
    filteredLogs() {
      let filtered = this.logs || []
      
      // 按日志级别过滤
      if (this.selectedLogLevel) {
        filtered = filtered.filter(log => log.level === this.selectedLogLevel)
      }
      
      // 按搜索查询过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(log => 
          log.message.toLowerCase().includes(query) ||
          log.source.toLowerCase().includes(query)
        )
      }
      
      return filtered.slice(0, 100) // 只显示前100条
    },
    totalLogs() {
      return this.logs ? this.logs.length : 0
    },
    errorLogs() {
      return this.logs ? this.logs.filter(log => log.level === 'ERROR' || log.level === 'CRITICAL').length : 0
    },
    warningLogs() {
      return this.logs ? this.logs.filter(log => log.level === 'WARNING').length : 0
    },
    latestLogTime() {
      if (!this.logs || this.logs.length === 0) return '无日志'
      const latest = this.logs[this.logs.length - 1]
      return latest.timestamp || 'N/A'
    }
  },
  methods: {
    getRowClass(level) {
      return `log-row-${level.toLowerCase()}`
    },
    viewLogDetails(log) {
      this.$emit('view-log-details', log)
    }
  }
}
</script>

<style scoped>
.log-visualizer {
  background: var(--card-bg);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.log-controls {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: end;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-section label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.log-level-select, .time-range-select, .search-input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--input-bg);
  color: var(--text-primary);
}

.search-input {
  min-width: 200px;
}

.log-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg-secondary);
  padding: 15px;
  border-radius: 6px;
  text-align: center;
}

.stat-card h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-number {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
}

.error-count {
  color: #e74c3c;
}

.warning-count {
  color: #f1c40f;
}

.log-chart {
  margin-bottom: 20px;
}

.log-chart h4 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.chart-container {
  background: var(--bg-secondary);
  padding: 15px;
  border-radius: 6px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-chart {
  text-align: center;
  color: var(--text-secondary);
}

.log-table-container {
  overflow-x: auto;
}

.log-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-secondary);
  border-radius: 6px;
  overflow: hidden;
}

.log-table th {
  background: var(--card-bg);
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 2px solid var(--border-color);
}

.log-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.log-table tr:last-child td {
  border-bottom: none;
}

.log-table tr:hover {
  background: var(--hover-bg);
}

.log-row-error, .log-row-critical {
  background: rgba(231, 76, 60, 0.05);
}

.log-row-warning {
  background: rgba(241, 196, 15, 0.05);
}

.log-level {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.log-level.info {
  background: rgba(52, 152, 219, 0.2);
  color: #3498db;
}

.log-level.warning {
  background: rgba(241, 196, 15, 0.2);
  color: #f1c40f;
}

.log-level.error {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.log-level.critical {
  background: rgba(192, 57, 43, 0.2);
  color: #c0392b;
}

.log-message {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.btn-small {
  padding: 4px 8px;
  font-size: 11px;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-outline:hover {
  background: var(--bg-secondary);
}

@media (max-width: 768px) {
  .log-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .log-stats {
    grid-template-columns: 1fr 1fr;
  }
  
  .search-input {
    min-width: auto;
  }
}
</style>