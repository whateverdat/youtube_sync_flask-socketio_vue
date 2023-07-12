import { createRouter, createWebHistory } from 'vue-router';
import Home from './pages/Home.vue';
import Room from './pages/Room.vue';

const router = createRouter({
  history: createWebHistory(),
  mode: 'history',
  routes: [
    { path: '/', component: Home },
    { path: '/:slug', component: Room },
  ],
});

let currentURL = window.location.href.split('/');
if (currentURL.length > 4) {
  window.location.href = `http://localhost:5173/${currentURL[3]}`;
}

export default router;
