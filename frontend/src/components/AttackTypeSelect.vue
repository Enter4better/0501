<template>
  <el-select 
    v-model="selectedType" 
    placeholder="选择攻击类型" 
    style="width: 100%;"
    filterable
    @change="handleChange"
    class="attack-type-select"
  >
    <el-option-group label="🌐 Web漏洞攻击">
      <el-option v-for="item in webAttacks" :key="item.value" :label="item.label" :value="item.value">
        <div class="attack-option-row">
          <span class="attack-name">{{ item.label }}</span>
          <el-tag size="small" :type="item.tagType" effect="dark" class="attack-tag">{{ item.level }}</el-tag>
        </div>
      </el-option>
    </el-option-group>
    <el-option-group label="💻 系统层攻击">
      <el-option v-for="item in systemAttacks" :key="item.value" :label="item.label" :value="item.value">
        <div class="attack-option-row">
          <span class="attack-name">{{ item.label }}</span>
          <el-tag size="small" :type="item.tagType" effect="dark" class="attack-tag">{{ item.level }}</el-tag>
        </div>
      </el-option>
    </el-option-group>
    <el-option-group label="🔗 网络攻击">
      <el-option v-for="item in networkAttacks" :key="item.value" :label="item.label" :value="item.value">
        <div class="attack-option-row">
          <span class="attack-name">{{ item.label }}</span>
          <el-tag size="small" :type="item.tagType" effect="dark" class="attack-tag">{{ item.level }}</el-tag>
        </div>
      </el-option>
    </el-option-group>
    <el-option-group label="🎯 高级持续性威胁">
      <el-option v-for="item in aptAttacks" :key="item.value" :label="item.label" :value="item.value">
        <div class="attack-option-row">
          <span class="attack-name">{{ item.label }}</span>
          <el-tag size="small" :type="item.tagType" effect="dark" class="attack-tag">{{ item.level }}</el-tag>
        </div>
      </el-option>
    </el-option-group>
  </el-select>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedType = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  selectedType.value = val
})

// Web漏洞攻击
const webAttacks = [
  { label: 'SQL注入', value: 'SQL注入', tagType: 'danger', level: '高危' },
  { label: 'XSS跨站脚本', value: 'XSS攻击', tagType: 'warning', level: '中危' },
  { label: 'CSRF跨站请求伪造', value: 'CSRF攻击', tagType: 'warning', level: '中危' },
  { label: '文件包含漏洞', value: '文件包含', tagType: 'danger', level: '高危' },
  { label: '命令执行', value: '命令执行', tagType: 'danger', level: '高危' },
  { label: 'SSRF服务端请求伪造', value: 'SSRF攻击', tagType: 'warning', level: '中危' },
  { label: 'XXE外部实体注入', value: 'XXE注入', tagType: 'danger', level: '高危' }
]

// 系统层攻击
const systemAttacks = [
  { label: '权限提升', value: '权限提升', tagType: 'danger', level: '高危' },
  { label: '容器逃逸', value: '容器逃逸', tagType: 'danger', level: '高危' },
  { label: '反弹Shell', value: '反弹Shell', tagType: 'danger', level: '高危' }
]

// 网络攻击
const networkAttacks = [
  { label: '端口扫描', value: '端口扫描', tagType: 'info', level: '信息收集' },
  { label: '暴力破解', value: '暴力破解', tagType: 'danger', level: '高危' },
  { label: '中间人攻击', value: '中间人攻击', tagType: 'danger', level: '高危' }
]

// APT攻击
const aptAttacks = [
  { label: '后门植入', value: '后门植入', tagType: 'danger', level: '高危' },
  { label: '横向移动', value: '横向移动', tagType: 'danger', level: '高危' },
  { label: '数据外传', value: '数据外传', tagType: 'danger', level: '高危' }
]

// 默认端口映射
const portMap = {
  'SQL注入': '3306', 'XSS攻击': '80', 'CSRF攻击': '80', '文件包含': '80',
  '命令执行': '80', 'SSRF攻击': '80', 'XXE注入': '80',
  '权限提升': '22', '容器逃逸': '22', '反弹Shell': '4444',
  '端口扫描': '1-1000', '暴力破解': '22', '中间人攻击': '80',
  '后门植入': '4444', '横向移动': '22', '数据外传': '80'
}

function handleChange(val) {
  emit('update:modelValue', val)
  emit('change', val, portMap[val] || '80')
}
</script>

<style scoped>
.attack-option-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.attack-name {
  font-size: 14px;
}

.attack-tag {
  margin-left: 8px;
}
</style>