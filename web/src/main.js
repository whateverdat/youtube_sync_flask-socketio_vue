import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import router from './routes';
// Pages
import Home from './pages/Home.vue';
import Room from './pages/Room.vue';
// Components
import DarkMode from './components/DarkMode.vue';
import Nav from './components/Nav.vue';
// import Access from './components/Access.vue';

const app = createApp(App);
app.use(router);

// Components
app.component('DarkMode', DarkMode);
app.component('Nav', Nav);
// app.component('Access', Access);

// Pages
app.component('Home', Home);
app.component('Room', Room);

const mountedApp = app.mount('#app');
