import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:5000/api/v1',  // 设置为你发送命令的地址
  timeout: 15000
});


export default {
  resource: (resourcePath) => ({
    create: (payload) => apiClient.post(`/${resourcePath}`, payload)
  })
}