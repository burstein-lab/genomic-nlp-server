import SpaceMap from "@/components/SpaceMap.vue";
const routes = [{ path: "/", component: SpaceMap }];

import { createRouter, createWebHashHistory } from "vue-router";

export default createRouter({
  history: createWebHashHistory(),
  routes,
});
