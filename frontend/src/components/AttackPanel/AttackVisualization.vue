<template>
  <div class="attack-visualization">
    <div class="timeline-container">
      <h3>攻击时间线</h3>
      <AttackTimeline :attacks="attacks" />
    </div>
    
    <div class="queue-container">
      <h3>攻击队列</h3>
      <AttackQueue :queue="attackQueue" />
    </div>
  </div>
</template>

<script>
import AttackTimeline from '@/components/AttackTimeline.vue'
import AttackQueue from '@/components/AttackQueue.vue'

export default {
  name: 'AttackVisualization',
  components: {
    AttackTimeline,
    AttackQueue
  },
  props: {
    attacks: Array,
    attackQueue: Array
  }
}
</script>

<style scoped>
.attack-visualization {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.timeline-container, .queue-container {
  background: var(--card-bg);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .attack-visualization {
    grid-template-columns: 1fr;
  }
}
</style>