import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Database from '../views/Database/Index.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/ai-assistant',
    name: 'AIAssistant',
    component: () => import('@/views/AIAssistant.vue')
  },
  {
    path: '/database',
    name: 'Database',
    component: () => import('@/views/Database.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
