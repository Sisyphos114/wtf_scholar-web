<template>
  <el-container>
    <el-header>
      <el-menu 
        mode="horizontal"
        :default-active="$route.path"
        router
        class="navigation-bar">
        <el-menu-item index="/outline">大纲输入</el-menu-item>
        <el-menu-item index="/literature">文献引用</el-menu-item>
        <el-menu-item index="/content">内容生成</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<style>
.navigation-bar {
  justify-content: center;
  border-bottom: none;
}

/* 在全局样式文件添加 */
html, body, #app {
  height: 80%;
  margin: 0;
  padding: 0;
}
/* 在全局样式添加 */
.el-message--error {
  font-size: 16px;
  min-width: 280px;
  padding: 15px 20px;
}
</style>