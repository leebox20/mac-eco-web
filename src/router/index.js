import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Database from '../views/Database/Index.vue'
import AnalysisResult from '@/views/AnalysisResult.vue'
import AnalysisPredictResult from '@/views/AnalysisPredictResult.vue'

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
  },
  {
    path: '/analysis-result',
    name: 'analysis-result',
    component: () => import('@/views/AnalysisResult.vue')
  },
  {
    path: '/prediction',
    name: 'Prediction',
    component: () => import('@/views/Prediction.vue')
  },
  {
    path: '/analysis-prediction/:indicatorId',
    name: 'AnalysisPredictResult',
    component: () => import('@/views/AnalysisPredictResult.vue'),
    props: true
  }  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
