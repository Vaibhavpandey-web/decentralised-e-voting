import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import VoteView from '../views/VoteView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue' // 🟢 NEW

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/setup', name: 'setup', component: () => import('../views/SetupView.vue') },
    { path: '/', name: 'home', component: HomeView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/vote', name: 'vote', component: VoteView },
    { path: '/admin-dashboard', name: 'adminDashboard', component: AdminDashboardView } // 🟢 NEW
  ]
})

export default router