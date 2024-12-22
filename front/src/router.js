// router.js
import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '@/components/LoginPage.vue';
import RegisterPage from '@/components/RegisterPage.vue';
import AdminDashboard from '@/components/AdminDashboard.vue';
import ClientDashboard from '@/components/ClientDashboard.vue';
import SettingsPage from '@/components/SettingsPage.vue';
import MallMap from '@/components/MallMap.vue';

const routes = [
  {
    path: '/login',
    component: LoginPage,
    meta: {
    }
  },
  { 
    path: '/register',
    component: RegisterPage,
    meta: {
    }
  },
  {
    path: '/clients', redirect: '/'
  },
  {
    path: '/admins', redirect: '/'
  },
  { 
    path: '/clients/profile',
    component: ClientDashboard,
    meta: {
        requiresAuth: true,
        role: 'client'
    }
  },
  { 
    path: '/clients/profile/settings',
    component: SettingsPage,
    meta: {
        requiresAuth: true,
        role: 'client'
    }
  },
  { 
    path: '/admins/:adminId',
    component: AdminDashboard,
    meta: {
        requiresAuth: true,
        role: 'admin'
    }
  },
  { 
    path: '/admins/:adminId/settings',
    component: SettingsPage,
    meta: {
        requiresAuth: true,
        role: 'admin'
    }
  },
  { 
    path: '/admins/profile/settings',
    component: SettingsPage,
    meta: {
        requiresAuth: true,
        role: 'admin'
    }
  },
  {
    path: '/malls', redirect: '/'
  },
  {
    path: '/malls/:mallId',
    component: MallMap,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/home', redirect: '/login'
  },
  { 
    path: '/', redirect: '/login'
  }
];

const router = createRouter({
  history: createWebHistory(), 
  routes
});

router.beforeEach((to, from, next) => {
  let user;
  try {
      user = JSON.parse(localStorage.getItem('user'));
  } catch (e) {
      user = null;
  }
  const isAuthenticated = !!user;
  const isAdmin = !!user && user.role === 'admin';

  if (to.path === '/login' && isAuthenticated) {
    if (isAdmin) {
      return next(`/${user.role}s/${user.id}`);
    }
    return next(`/${user.role}s/profile`);
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
    return;
  } 
  if (to.meta.role === 'admin' && !isAdmin) {
    next('/home');
    return;
  }

  if (to.params.adminId && Number(to.params.adminId) !== Number(user.id)) {
    return next('/home');
  }

  if (to.params.clientId && Number(to.params.clientId) !== Number(user.id) && user.role === 'client') {
    return next('/home');
  }

  if (to.params.clientId && Number(to.params.clientId) === Number(user.id) && user.role === 'admin') {
    return next('/home');
  }

  if (to.path === '/admins/profile/settings') {
    return next(`/admins/${user.id}/settings`);
  }
  // document.title = to.meta.title;
  next();
})

// router.afterEach((to, from) => {
//   document.title = to.path;
// })

export default router;