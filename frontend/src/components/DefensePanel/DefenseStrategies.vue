<template>
  <div class="defense-strategies">
    <h3>防御策略</h3>
    
    <div class="strategy-controls">
      <button @click="toggleAutoDefense" class="btn btn-primary">
        {{ autoDefenseEnabled ? '关闭自动防御' : '开启自动防御' }}
      </button>
      <select v-model="selectedStrategy" class="strategy-select">
        <option value="">选择防御策略</option>
        <option v-for="strategy in availableStrategies" :key="strategy.value" :value="strategy.value">
          {{ strategy.label }}
        </option>
      </select>
      <button @click="applyStrategy" class="btn btn-secondary" :disabled="!selectedStrategy">
        应用策略
      </button>
    </div>
    
    <div class="strategy-grid">
      <div 
        v-for="strategy in defenseStrategies" 
        :key="strategy.id"
        class="strategy-card"
        :class="{ active: strategy.active, disabled: !strategy.enabled }"
      >
        <div class="strategy-header">
          <h4>{{ strategy.name }}</h4>
          <div class="strategy-status">
            <span class="status-badge" :class="strategy.status">{{ strategy.status }}</span>
          </div>
        </div>
        
        <div class="strategy-description">
          <p>{{ strategy.description }}</p>
        </div>
        
        <div class="strategy-metrics">
          <div class="metric">
            <span class="metric-label">有效性:</span>
            <span class="metric-value">{{ strategy.effectiveness }}%</span>
          </div>
          <div class="metric">
            <span class="metric-label">资源消耗:</span>
            <span class="metric-value">{{ strategy.resourceUsage }}%</span>
          </div>
        </div>
        
        <div class="strategy-actions">
          <button 
            @click="toggleStrategy(strategy)" 
            class="btn"
            :class="strategy.active ? 'btn-danger' : 'btn-success'"
          >
            {{ strategy.active ? '停用' : '启用' }}
          </button>
          <button @click="viewStrategyDetails(strategy)" class="btn btn-outline">
            详情
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DefenseStrategies',
  props: {
    defenseStrategies: Array,
    autoDefenseEnabled: Boolean
  },
  emits: ['toggle-auto-defense', 'apply-strategy', 'toggle-strategy', 'view-details'],
  data() {
    return {
      selectedStrategy: '',
      availableStrategies: [
        { value: 'waf', label: 'Web应用防火墙' },
        { value: 'ips', label: '入侵防护系统' },
        { value: 'ids', label: '入侵检测系统' },
        { value: 'firewall', label: '网络防火墙' },
        { value: 'rate_limiting', label: '速率限制' },
        { value: 'anomaly_detection', label: '异常检测' }
      ]
    }
  },
  methods: {
    toggleAutoDefense() {
      this.$emit('toggle-auto-defense')
    },
    applyStrategy() {
      if (this.selectedStrategy) {
        this.$emit('apply-strategy', this.selectedStrategy)
        this.selectedStrategy = ''
      }
    },
    toggleStrategy(strategy) {
      this.$emit('toggle-strategy', strategy)
    },
    viewStrategyDetails(strategy) {
      this.$emit('view-details', strategy)
    }
  }
}
</script>

<style scoped>
.defense-strategies {
  background: var(--card-bg);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.strategy-controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-secondary {
  background: var(--secondary-color);
  color: white;
}

.btn-secondary:hover {
  background: var(--secondary-hover);
}

.btn-success {
  background: #2ecc71;
  color: white;
}

.btn-success:hover {
  background: #27ae60;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-outline:hover {
  background: var(--bg-secondary);
}

.strategy-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--input-bg);
  color: var(--text-primary);
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.strategy-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s ease;
}

.strategy-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.strategy-card.active {
  border-color: #2ecc71;
  background: rgba(46, 204, 113, 0.05);
}

.strategy-card.disabled {
  opacity: 0.6;
  filter: grayscale(50%);
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.strategy-header h4 {
  margin: 0;
  color: var(--text-primary);
}

.strategy-status {
  display: flex;
  align-items: center;
  gap: 5px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.status-badge.active {
  background: rgba(46, 204, 113, 0.2);
  color: #2ecc71;
}

.status-badge.inactive {
  background: rgba(149, 165, 166, 0.2);
  color: #95a5a6;
}

.strategy-description {
  margin-bottom: 15px;
}

.strategy-description p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.4;
}

.strategy-metrics {
  margin-bottom: 15px;
}

.metric {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 13px;
}

.metric-label {
  color: var(--text-secondary);
}

.metric-value {
  font-weight: bold;
  color: var(--text-primary);
}

.strategy-actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .strategy-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .strategy-grid {
    grid-template-columns: 1fr;
  }
  
  .strategy-actions {
    flex-direction: column;
  }
}
</style>