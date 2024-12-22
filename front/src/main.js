// main.js
import { createApp } from 'vue';
import App from '@/App.vue';
import router from '@/router';
import axios from 'axios';
import '@/styles/global.css';

const app = createApp(App);

app.config.globalProperties.$axios = axios;
app.config.globalProperties.$axios.defaults.baseURL = 'http://' + '127.0.0.1' + ':5000' // 192.168.88.137 192.168.90.94 127.0.0.1

app.use(router);

// Монтируем приложение в элемент с id="app"
app.mount('#app');