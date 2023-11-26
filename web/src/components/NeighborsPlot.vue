<template>
  <BarChart class="mt-3" :chartData="chartData()" :options="options()" />
</template>

<script lang="ts">
import { BarChart } from "vue-chart-3";
import { spaceToInfo, Space, SpacesReponse } from "@/composables/spaces";

import { useTheme } from "vuetify";

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
  data: () => {
    return {
      theme: useTheme(),
    };
  },
  emits: ["click"],
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
          legend: {
            display: false,
            labels: {
              color: this.theme.global.current.dark ? "#FFFFFF" : "#000000",
            },
          },
          tooltip: {
            callbacks: {
              title: () => null,
              footer: (items: any) => this.hover(items[0]),
            },
          },
        },
        onClick: (e: ChartEvent) => {
          // Found example in https://masteringjs.io/tutorials/chartjs/onclick-bar-chart
          const res = e.chart.getElementsAtEventForMode(
            e,
            "nearest",
            { intersect: true },
            true
          );

          if (res.length === 0) {
            return;
          }

          this.$emit("click", this.data.spaces[res[0].index].value.word);
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

interface ChartEvent extends Event {
  chart: Chart;
}
</script>
