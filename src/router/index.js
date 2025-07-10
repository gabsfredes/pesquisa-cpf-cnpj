import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import Home from '../pages/Home.vue'
import Config from '../pages/Config.vue'
import Register from '../pages/Register.vue'
import { useAuthStore } from '../store/auth'
import { useConfigStore } from '../store/config'

const routes = [
  { path: '/config', component: Config },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  {
    path: '/',
    component: Home,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const config = useConfigStore()

  if (!config.configurado && to.path !== '/config') {
    return next('/config')
  }

  if (to.meta.requiresAuth && !auth.token) {
    return next('/login')
  }

  return next()
})

export default router
