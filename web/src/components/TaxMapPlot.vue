<template>
  <DoughnutChart class="mt-3" :chartData="chartData()" :options="options()" />
</template>

<script lang="ts">
import { DoughnutChart } from "vue-chart-3";
import { spaceToInfo, Space, SpacesReponse } from "@/composables/spaces";

import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

export default {
  name: "TaxMapPlot",
  components: {
    DoughnutChart,
  },
  props: {
    data: {
      type: Object as () => [string, number][],
      required: true,
    },
  },
  data: () => {
    return {
      palette: [
        "#a6cee3",
        "#33a02c",
        "#fb9a99",
        "#e31a1c",
        "#fdbf6f",
        "#6a3d9a",
        "#ffff99",
        "#b15928",
        "#b2df8a",
        "#1f78b4",
        "#808080",
      ],
    };
  },
  methods: {
    options() {
      return {
        cutoutPercentage: 50, // Adjust as needed
        legend: {
          position: "right",
        },
        title: {
          display: true,
          text: "Taxonomy distribution (order)",
        },
      };
    },
    chartData() {
      const [labels, values] = this.data[0].map((_, colIndex) =>
        this.data.map((row) => row[colIndex])
      );
      return {
        labels: labels,
        datasets: [
          {
            data: values,
            backgroundColor: this.palette,
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
