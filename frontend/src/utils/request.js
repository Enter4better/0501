import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' }
})

request.interceptors.response.use(
  res => res.data,
  err => {
    console.error('API Error:', err.message)
    return Promise.reject(err)
  }
)

export default request
