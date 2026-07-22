import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Add this line

const app = createApp(App)

app.use(router) // Add this line
app.mount('#app')