<template>
  <el-card class="reference-container">
    <template #header>
      <h2>文献引用管理</h2>
    </template>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="本地数据库" name="local">
        <el-upload
          class="upload-container"
          action="/api/v1/process/link_refs"
          :show-file-list="false"
          :on-success="handleUploadSuccess">
          <el-button type="primary">上传文献数据库</el-button>
        </el-upload>
      </el-tab-pane>

      <el-tab-pane label="在线搜索" name="online">
        <el-input
          v-model="searchKey"
          placeholder="输入论文关键词"
          class="search-input">
          <template #append>
            <el-button @click="searchPapers">搜索</el-button>
          </template>
        </el-input>
        
        <div v-if="searchResults.length" class="results-container">
          <el-checkbox-group v-model="selectedPapers">
            <el-checkbox 
              v-for="paper in searchResults" 
              :key="paper.id"
              :label="paper.id">
              {{ paper.title }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </el-tab-pane>
    </el-tabs>

    <div class="action-buttons">
      <el-button 
        type="success"
        @click="completeReferences"
        :disabled="!canComplete">
        完成
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const activeTab = ref('local')
const searchKey = ref('')
const searchResults = ref([])
const selectedPapers = ref([])
const router = useRouter()

const canComplete = computed(() => {
  return activeTab.value === 'local' || selectedPapers.value.length > 0
})

const searchPapers = async () => {
  const response = await axios.post('/api/v1/process/link_refs', {
    key: searchKey.value
  })
  searchResults.value = response.data.results
}

const handleUploadSuccess = (response) => {
  ElMessage.success('文献数据库上传成功')
}

const completeReferences = () => {
  router.push('/content')
}
</script>