import request from '@/utils/request'

// 认证相关API
export const authApi = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data),
  logout: () => request.post('/auth/logout'),
  getProfile: () => request.get('/auth/profile'),
  updateProfile: (data) => request.put('/auth/profile', data),
  changePassword: (data) => request.post('/auth/change-password', data),
  getUsers: () => request.get('/auth/users')
}

// 环境管理API
export const targetApi = {
  getAll: () => request.get('/env/list'),
  getById: (id) => request.get(`/env/${id}`),
  create: (data) => request.post('/env/create', data),
  update: (id, data) => request.put(`/env/${id}`, data),
  delete: (id) => request.post(`/env/delete/${id}`),
  start: (id) => request.post(`/env/start/${id}`),
  stop: (id) => request.post(`/env/stop/${id}`),
  restart: (id) => request.post(`/env/restart/${id}`),
  getStatus: (id) => request.get(`/env/${id}/status`),
  clean: () => request.post('/env/clean'),
  stats: () => request.get('/env/stats'),
  getImages: () => request.get('/env/images')
}

// 攻击管理API
export const attackApi = {
  getAll: () => request.get('/attack/list'),
  getById: (id) => request.get(`/attack/${id}`),
  create: (data) => request.post('/attack/create', data),
  update: (id, data) => request.put(`/attack/${id}`, data),
  delete: (id) => request.delete(`/attack/${id}`),
  execute: (id) => request.post(`/attack/execute/${id}`),
  stop: (id) => request.post(`/attack/stop/${id}`),
  getResult: (id) => request.get(`/attack/result/${id}`),
  batchExecute: (ids) => request.post('/attack/batch-execute', { attack_ids: ids }),
  getTypes: () => request.get('/attack/types'),
  getStats: () => request.get('/attack/stats'),
  getTemplates: () => request.get('/attack/templates'),
  executeTemplate: (name, data) => request.post(`/attack/template/execute/${name}`, data),
  getLogs: (id) => request.get(`/attack/${id}/logs`)
}

// 防御管理API
export const defenseApi = {
  getAll: () => request.get('/defense/list'),
  getById: (id) => request.get(`/defense/${id}`),
  create: (data) => request.post('/defense/create', data),
  update: (id, data) => request.put(`/defense/update/${id}`, data),
  delete: (id) => request.delete(`/defense/delete/${id}`),
  toggle: (id) => request.post(`/defense/toggle/${id}`),
  check: (data) => request.post('/defense/check', data),
  getResult: (id) => request.get(`/defense/result/${id}`),
  getStats: () => request.get('/defense/stats'),
  getTypes: () => request.get('/defense/types'),
  getTemplates: () => request.get('/defense/templates'),
  applyTemplate: (name) => request.post(`/defense/template/apply/${name}`)
}

// 日志管理API
export const logApi = {
  getAll: (params) => request.get('/logs/list', { params }),
  getById: (id) => request.get(`/logs/${id}`),
  getStats: () => request.get('/logs/stats'),
  export: (params) => request.get('/logs/export', { params, responseType: 'blob' }),
  clear: () => request.delete('/logs/clear')
}

// 统计数据API
export const statsApi = {
  getStats: () => request.get('/stats'),
  getDashboard: () => request.get('/stats/dashboard'),
  getHealth: () => request.get('/stats/health')
}

// AI决策API
export const aiApi = {
  generateSummary: (data) => request.post('/ai/summary', data),
  analyzeThreat: (data) => request.post('/ai/analyze', data),
  applyDefense: () => request.post('/ai/apply-defense'),
  blockThreats: (data) => request.post('/ai/block-threats', data),
  blockThreat: (data) => request.post('/ai/block-threat', data),
  getRecommendations: () => request.get('/ai/recommendations'),
  chat: (data) => request.post('/ai/chat', data)
}

// 拓扑管理API
export const topologyApi = {
  getTopology: () => request.get('/topology/'),
  pingNode: (data) => request.post('/topology/ping', data),
  sshNode: (data) => request.post('/topology/ssh', data),
  restartNode: (data) => request.post('/topology/restart', data),
  scanNetwork: () => request.post('/topology/scan'),
  checkConnectivity: () => request.get('/topology/connectivity'),
  getFlowData: () => request.get('/topology/flow')
}

// AI Agent API
export const agentApi = {
  // 环境管理Agent
  env: {
    getScenarios: () => request.get('/agents/env/scenarios'),
    analyzeScenario: (data) => request.post('/agents/env/analyze', data),
    createEnvironment: (data) => request.post('/agents/env/create', data),
    getStatus: (envId) => request.get(`/agents/env/status/${envId}`),
    destroyEnvironment: (envId) => request.post(`/agents/env/destroy/${envId}`)
  },
  // 攻击模拟Agent
  attack: {
    getTypes: () => request.get('/agents/attack/types'),
    getPhases: () => request.get('/agents/attack/phases'),
    planAttack: (data) => request.post('/agents/attack/plan', data),
    executeAttack: (data) => request.post('/agents/attack/execute', data),
    generateReport: (data) => request.post('/agents/attack/report', data)
  },
  // 防御模拟Agent
  defense: {
    getTypes: () => request.get('/agents/defense/types'),
    getActions: () => request.get('/agents/defense/actions'),
    analyzeThreat: (data) => request.post('/agents/defense/analyze', data),
    deployDefense: (data) => request.post('/agents/defense/deploy', data),
    detectAttack: (data) => request.post('/agents/defense/detect', data),
    respondToAttack: (data) => request.post('/agents/defense/respond', data),
    checkDefense: (data) => request.post('/agents/defense/check', data),
    getAlerts: () => request.get('/agents/defense/alerts'),
    clearAlerts: () => request.post('/agents/defense/alerts/clear'),
    getBlockedIps: () => request.get('/agents/defense/blocked-ips'),
    generateReport: (data) => request.post('/agents/defense/report', data)
  },
  // 综合功能
  runFullSimulation: (data) => request.post('/agents/full-simulation', data),
  getStatus: () => request.get('/agents/status')
}

export default {
  auth: authApi,
  target: targetApi,
  attack: attackApi,
  defense: defenseApi,
  log: logApi,
  stats: statsApi,
  ai: aiApi,
  topology: topologyApi,
  agent: agentApi
}
