<template>
  <BarChart class="mt-3" :chartData="chartData()" :options="options()" />
</template>

<script lang="ts">
import { BarChart } from "vue-chart-3";
import { spaceToInfo, Space, SpacesReponse } from "@/composables/spaces";

import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

export default {
  name: "NeighborsPlot",
  components: {
    BarChart,
  },
  props: {
    data: {
      type: Object as () => SpacesReponse,
      required: true,
    },
  },
  methods: {
    hover(item: any) {
      const infoMap = spaceToInfo(this.data.spaces[item.dataIndex].value);
      return Array.from(infoMap, ([key, value]) => `${key}: ${value}`);
    },
    options() {
      return {
        title: { display: false },
        scales: { y: { title: { display: true, text: "Similarity" } } },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: () => null,
              footer: (items: any) => this.hover(items[0]),
            },
          },
        },
      };
    },
    chartData() {
      const x: string[] = [];
      const y: Number[] = [];
      this.data.spaces.forEach((space: Space) => {
        x.push(space.value.word);
        y.push(space.value.distance);
      });
      return {
        labels: x,
        datasets: [
          {
            data: y,
            backgroundColor: "#da4ca4",
          },
        ],
      };
    },
  },
};
</script>
