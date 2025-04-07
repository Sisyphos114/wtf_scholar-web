import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/outline'
  },
  {
    path: '/outline',
    component: () => import('../views/OutlineInput.vue')
  },
  {
    path: '/literature',
    component: () => import('../views/LiteratureReference.vue')
  },
  {
    path: '/content',
    component: () => import('../views/ContentGeneration.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router