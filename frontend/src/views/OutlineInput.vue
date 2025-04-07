<template>
  <el-card class="outline-container">
    <template #header>
      <h2>论文大纲输入</h2>
    </template>
    
    <el-input
        v-model="outlineText"
        type="textarea"
        :autosize="{ minRows: 15, maxRows: 25 }"
        placeholder="请输入论文大纲..."
        class="full-height-textarea"
    />
    
    <div class="action-buttons">
      <el-button 
        type="primary"
        @click="submitOutline"
        :loading="isSubmitting">
        下一步
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/services/api' // 封装后的API服务

const outlineText = ref('')
const isSubmitting = ref(false)
const router = useRouter()

// RESTful 风格提交
const submitOutline = async () => {
  if (!outlineText.value.trim()) {
    ElMessage.error('论文大纲内容不能为空')
    return
  }

  try {
    isSubmitting.value = true
    
    // 将大纲文本发送为 JSON 格式
    const payload = {
      outline: outlineText.value.trim()
    }

    // 使用封装的 API 请求提交数据
    const { data } = await api.resource('outlines').create(payload)

    // 状态码处理
    if (data.id) { // 标准RESTful返回创建的资源ID
      await router.push({
        name: 'LiteratureReference',
        params: { outlineId: data.id } // 资源ID传递
      })
      ElMessage.success(`大纲创建成功，ID: ${data.id}`)
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    isSubmitting.value = false
  }
}

// 统一错误处理方法
const handleApiError = (error) => {
  const status = error.response?.status
  const errorData = error.response?.data || {}
  
  // RESTful 标准状态码处理
  switch(status) {
    case 400:
      ElMessage.error(`请求错误: ${errorData.message || '参数校验失败'}`)
      break
    case 401:
      router.push('/login') // 跳转认证
      break
    case 403:
      ElMessage.warning('操作权限不足')
      break
    case 404:
      ElMessage.error('资源不存在')
      break
    case 422:
      showValidationErrors(errorData.errors) // 表单验证错误
      break
    default:
      ElMessage.error(`系统错误: ${status || '网络连接异常'}`)
  }
}

// 显示详细验证错误
const showValidationErrors = (errors) => {
  if (errors) {
    const messages = Object.values(errors).flat()
    ElMessage.error({
      message: '验证失败',
      grouping: true,
      duration: 3000,
      dangerouslyUseHTMLString: true,
      message: `<ul>${messages.map(e => `<li>${e}</li>`).join('')}</ul>`
    })
  }
}
</script>

<script>
// api.js 服务封装
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1', // 基础 URL 配置
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json', // 请求类型为 JSON
    'Accept': 'application/json'        // 接受 JSON 格式的响应
  }
})

// 请求拦截器（认证处理）
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken')  // 从本地存储中获取 token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`  // 设置 Authorization 头
  }
  return config
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    // 处理分页数据
    if (response.data?.pagination) {
      return {
        data: response.data.items,
        pagination: response.data.pagination
      }
    }
    return response.data
  },
  error => {
    return Promise.reject(error)  // 错误处理
  }
)

// RESTful 资源封装
const resource = (resourcePath) => ({
  create(payload) {
    return apiClient.post(`/${resourcePath}`, payload) // 创建资源
  },
  get(id) {
    return apiClient.get(`/${resourcePath}/${id}`) // 获取单个资源
  },
  update(id, payload) {
    return apiClient.put(`/${resourcePath}/${id}`, payload) // 更新资源
  },
  delete(id) {
    return apiClient.delete(`/${resourcePath}/${id}`) // 删除资源
  },
  list(params) {
    return apiClient.get(`/${resourcePath}`, { params }) // 获取资源列表
  }
})

export default { resource }
</script>
