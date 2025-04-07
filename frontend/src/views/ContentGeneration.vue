<template>
  <el-card class="content-container">
    <template #header>
      <h2>生成内容预览</h2>
    </template>

    <div v-loading="isLoading" class="generated-content">
      <textarea 
        v-model="generatedContent" 
        class="content-textarea" 
        placeholder="编辑文章内容..." 
        rows="15"
      ></textarea>
    </div>

    <div class="action-buttons">
      <el-button 
        type="primary" 
        @click="generateDocument"
        :loading="isGenerating"
      >
        生成文档
      </el-button>

      <el-button 
        type="primary" 
        @click="downloadContent"
        :loading="isDownloading"
      >
        导出文档
      </el-button>

      <el-button 
        type="success"
        @click="saveContent"
        :loading="isSaving"
      >
        保存文档
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const generatedContent = ref('')
const isLoading = ref(false)
const isDownloading = ref(false)
const isSaving = ref(false)
const isGenerating = ref(false)

// 加载初始内容
const fetchInitialContent = async () => {
  try {
    isLoading.value = true
    const response = await axios.get('http://localhost:5000/get-manuscript')
    if (response.headers['content-type'].includes('text')) {
      generatedContent.value = response.data || ''
    } else {
      ElMessage.error('加载的内容格式不正确')
    }
  } catch (error) {
    console.error('加载文档失败:', error)
    ElMessage.error('加载文档失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// 生成文档
const generateDocument = async () => {
  try {
    isGenerating.value = true
    const response = await axios.post('http://localhost:5000/run-scripts', {
      content: generatedContent.value
    })
    if (response.data.success) {
      ElMessage.success('文档生成成功')
      generatedContent.value = response.data.content || ''
    } else {
      ElMessage.error('文档生成失败')
    }

  } finally {
    isGenerating.value = false
  }
}

// 导出文档
const downloadContent = async () => {
  try {
    isDownloading.value = true
    // 直接使用编辑后的内容进行导出
    const exportResponse = await axios({
      method: 'POST',
      url: 'http://localhost:5000/export-doc',
      data: {
        content: generatedContent.value
      },
      responseType: 'blob'
    })

    if (exportResponse.status === 200) {
      const blob = new Blob([exportResponse.data], { type: 'application/msword' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'manuscript.docx')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      ElMessage.success('文档导出成功')
    }
  } catch (error) {
    console.error('文档导出失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    isDownloading.value = false
  }
}

// 保存文档
const saveContent = async () => {
  try {
    isSaving.value = true
    if (!generatedContent.value || generatedContent.value.trim() === '') {
      ElMessage.error('内容不能为空')
      return
    }
    const response = await axios.post('http://localhost:5000/save-manuscript', {
      content: generatedContent.value
    })
    if (response.data.success) {
      ElMessage.success('文档已保存')
    } else {
      ElMessage.error(`保存失败: ${response.data.message}`)
    }
  } catch (error) {
    console.error('文档保存失败:', error)
    ElMessage.error('保存失败，请稍后重试')
  } finally {
    isSaving.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchInitialContent()
})
</script>

<style scoped>
.content-container {
  margin: 20px;
}

.generated-content {
  min-height: 500px;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 20px;
}

.content-textarea {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  line-height: 1.5;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  resize: vertical;
}

.action-buttons {
  margin-top: 20px;
  text-align: right;
}

.action-buttons .el-button {
  margin-left: 10px;
}

.el-card__header {
  padding: 10px;
}

.el-card__body {
  padding: 20px;
}
</style>
