import { createRouter, createWebHashHistory } from "vue-router";
import HelloWorld from "../components/HelloWorld.vue";
import Ping from "../components/Ping.vue";
const routes = [
  {
    path: "/",
    name: "Home",
    component: HelloWorld,
  },
  {
    path: "/ping",
    name: "Ping",
    component: Ping,
  },
];
const router = createRouter({
  history: createWebHashHistory(),
  routes,
});
export default router;
