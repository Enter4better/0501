<template>
  <div :class="['stat-card-wrapper', cardClass]">
    <div class="stat-icon-wrapper">
      <el-icon :size="24"><component :is="icon" /></el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-value-text">{{ value }}</div>
      <div class="stat-label-text">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: Object, required: true },
  value: { type: [String, Number], default: '--' },
  label: { type: String, default: '' },
  type: { type: String, default: 'info' }
})

const cardClass = computed(() => `stat-type-${props.type}`)
</script>

<style scoped>
/* StatCard组件 - 科技风格亮色设计，无白边 */
.stat-card-wrapper {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(80, 144, 160, 0.45), rgba(96, 80, 160, 0.45));
  border: none;
  border-radius: 0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
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
  box-shadow: 0 4px 20px rgba(80, 144, 160, 0.25);
}

.stat-card-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(80, 144, 160, 0.1), rgba(96, 80, 160, 0.1));
  pointer-events: none;
}

.stat-card-wrapper:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(80, 144, 160, 0.35);
  background: linear-gradient(135deg, rgba(80, 144, 160, 0.55), rgba(96, 80, 160, 0.55));
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  color: #ffffff;
}

.stat-type-danger .stat-icon-wrapper {
  background: rgba(160, 64, 80, 0.35);
  color: #ffffff;
}

.stat-type-success .stat-icon-wrapper {
  background: rgba(64, 160, 96, 0.35);
  color: #ffffff;
}

.stat-type-warning .stat-icon-wrapper {
  background: rgba(160, 144, 32, 0.35);
  color: #ffffff;
}

.stat-type-info .stat-icon-wrapper {
  background: rgba(64, 128, 160, 0.35);
  color: #ffffff;
}

.stat-type-cyan .stat-icon-wrapper {
  background: rgba(80, 144, 160, 0.35);
  color: #ffffff;
}

.stat-type-purple .stat-icon-wrapper {
  background: rgba(96, 80, 160, 0.35);
  color: #ffffff;
}

.stat-content {
  display: flex;
  flex-direction: column;
  color: #ffffff;
}

.stat-value-text {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  font-family: 'Orbitron', 'Rajdhani', 'Exo 2', sans-serif;
  color: #ffffff;
}

.stat-label-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 4px;
  font-family: 'Rajdhani', 'Exo 2', 'Microsoft YaHei', sans-serif;
  letter-spacing: 0.3px;
}
</style>