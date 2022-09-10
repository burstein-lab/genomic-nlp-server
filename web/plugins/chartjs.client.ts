import { defineNuxtPlugin } from "#app";

// Workaround because chart.js doesn't provide an default export
import * as ChartJs from "chart.js";
const { Chart, registerables } = ChartJs;

export default defineNuxtPlugin(() => {
  Chart.register(...registerables);
});
