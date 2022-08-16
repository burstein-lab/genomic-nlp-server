import { createRouter, createWebHashHistory } from "vue-router";
import Static from "../components/Static.vue";
import Ping from "../components/Ping.vue";
import Map from "../components/Map.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Static,
  },
  {
    path: "/ping",
    name: "Ping",
    component: Ping,
  },
  {
    path: "/map",
    name: "Map",
    component: Map,
  },
];
const router = createRouter({
  history: createWebHashHistory(),
  routes,
});
export default router;
