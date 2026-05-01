<template>
  <div class="threat-detection">
    <div class="detection-header">
      <h3>威胁检测</h3>
      <div class="status-indicator" :class="getStatusClass">
        <span class="status-dot"></span>
        <span>{{ threatStatus }}</span>
      </div>
    </div>
    
    <div class="threat-metrics">
      <div class="metric-card">
        <h4>当前威胁等级</h4>
        <div class="threat-level" :class="currentThreatLevel.toLowerCase()">
          {{ currentThreatLevel }}
        </div>
      </div>
      
      <div class="metric-card">
        <h4>活跃威胁数量</h4>
        <div class="metric-value">{{ activeThreatsCount }}</div>
      </div>
      
      <div class="metric-card">
        <h4>检测准确率</h4>
        <div class="metric-value">{{ detectionAccuracy }}%</div>
      </div>
    </div>
    
    <div class="threat-list">
      <h4>最近检测到的威胁</h4>
      <div v-if="recentThreats.length === 0" class="no-threats">
        未检测到威胁
      </div>
      <div v-else class="threat-items">
        <div 
          v-for="threat in recentThreats" 
          :key="threat.id" 
          class="threat-item"
          :class="threat.severity.toLowerCase()"
        >
          <div class="threat-info">
            <span class="threat-type">{{ threat.type }}</span>
            <span class="threat-time">{{ threat.timestamp }}</span>
          </div>
          <div class="threat-details">
            <span class="threat-severity">严重程度: {{ threat.severity }}</span>
            <span class="threat-source">来源: {{ threat.source }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ThreatDetection',
  props: {
    threatStatus: String,
    currentThreatLevel: String,
    activeThreatsCount: Number,
    detectionAccuracy: Number,
    recentThreats: Array
  },
  computed: {
    getStatusClass() {
      return this.threatStatus.toLowerCase().replace(/\s+/g, '-');
    }
  }
}
</script>

<style scoped>
.threat-detection {
  background: var(--card-bg);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.detection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.status-indicator.normal {
  background: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.status-indicator.warning {
  background: rgba(241, 196, 15, 0.1);
  color: #f1c40f;
}

.status-indicator.alert {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator.normal .status-dot {
  background: #2ecc71;
}

.status-indicator.warning .status-dot {
  background: #f1c40f;
}

.status-indicator.alert .status-dot {
  background: #e74c3c;
}

.threat-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.metric-card {
  background: var(--bg-secondary);
  padding: 15px;
  border-radius: 6px;
  text-align: center;
}

.metric-card h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.threat-level {
  font-size: 24px;
  font-weight: bold;
  text-transform: uppercase;
}

.threat-level.low {
  color: #2ecc71;
}

.threat-level.medium {
  color: #f1c40f;
}

.threat-level.high {
  color: #e74c3c;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: var(--text-primary);
}

.threat-list h4 {
  margin: 0 0 15px 0;
  color: var(--text-primary);
}

.no-threats {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px;
  font-style: italic;
}

.threat-items {
  max-height: 200px;
  overflow-y: auto;
}

.threat-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  background: var(--bg-secondary);
  border-left: 4px solid;
}

.threat-item.low {
  border-left-color: #2ecc71;
}

.threat-item.medium {
  border-left-color: #f1c40f;
}

.threat-item.high {
  border-left-color: #e74c3c;
}

.threat-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.threat-type {
  font-weight: bold;
  color: var(--text-primary);
}

.threat-time {
  color: var(--text-secondary);
  font-size: 12px;
}

.threat-details {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .detection-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .threat-metrics {
    grid-template-columns: 1fr;
  }
}
</style>