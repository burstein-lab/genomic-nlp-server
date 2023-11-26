<template>
  <ScatterChart class="mt-3" :chartData="chartData()" :options="options()" />
</template>

<script lang="ts">
import { ScatterData } from "@/composables/spaces";
import { useTheme } from "vuetify";
import { ScatterChart } from "vue-chart-3";
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

export default {
  name: "PredictionPlot",
  components: {
    ScatterChart,
  },
  props: {
    data: {
      type: Object as () => ScatterData,
      required: true,
    },
  },
  data: () => {
    return {
      theme: useTheme(),
    };
  },
  methods: {
    hover(item: any) {
      return `${this.data.ticks[item.dataIndex]}: 1e${
        Math.round((item.parsed.y + Number.EPSILON) * 1000) / 1000
      }`;
    },
    options() {
      return {
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: (item: any) => this.hover(item),
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Predicted functional category",
            },
            ticks: {
              callback: (value: string, index: number, ticks: any[]) => {
                return this.data.ticks[index];
              },
            },
          },
          y: {
            title: {
              display: true,
              text: "Score",
            },
            ticks: {
              callback: (value: number, index: number, ticks: any[]) => {
                if (value === 0) return "1";
                return "1e" + value;
              },
            },
          },
        },
      };
    },
    chartData() {
      return {
        datasets: [
          {
            label: this.data.label,
            data: this.data.data,
            backgroundColor: "#da4ca4",
          },
        ],
      };
    },
  },
};
</script>
