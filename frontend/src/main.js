import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import Antd from 'ant-design-vue';
import App from "./App.vue";
import Home from "./views/Home.vue";
import Create from "./views/Create.vue";
import History from "./views/History.vue";
import Convert from "./views/Convert.vue";
import Login from "./views/Login.vue";
import User from "./views/User.vue";
import Settings from "./views/Settings.vue";
import Cover from "./views/Cover.vue";
import Presenter from "./views/Presenter.vue";
import TemplateHub from "./views/TemplateHub.vue";
import 'ant-design-vue/dist/reset.css';

const routes = [
  { path: "/", component: Home },
  { path: "/login", component: Login },
  { path: "/user", component: User },
  { path: "/settings", component: Settings },
  { path: "/create", component: Create },
  { path: "/history", component: History },
  { path: "/convert", component: Convert },
  { path: "/presenter/:filename", component: Presenter },
  { path: "/cover", component: Cover },
  { path: "/template-hub", component: TemplateHub },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('demoppt_token')
  const protectedRoutes = ['/create', '/user', '/history']
  
  if (protectedRoutes.includes(to.path) && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/user')
  } else {
    next()
  }
})

const app = createApp(App);
app.use(router);
app.use(Antd);
app.mount("#app");
