<template>
  <DoughnutChart class="mt-3" :chartData="chartData()" :options="options()" />
</template>

<script lang="ts">
import { DoughnutChart } from "vue-chart-3";
import { Chart, registerables } from "chart.js";
import { useTheme } from "vuetify";
Chart.register(...registerables);

export default {
  name: "TaxMapPlot",
  components: {
    DoughnutChart,
  },
  props: {
    tax_distribution: {
      type: Object as () => [string, number][],
      required: true,
    },
    tax_ratio: {
      type: Number,
      required: true,
    },
  },
  data: () => {
    return {
      theme: useTheme(),
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
        plugins: {
          legend: {
            labels: {
              color: this.theme.global.current.dark ? "#FFFFFF" : "#000000",
            },
          },
          subtitle: {
            display: true,
            text: `Percentage of genes with known taxonomy in database: ${this.tax_ratio}%`,
            color: this.theme.global.current.dark ? "#FFFFFF" : "#000000",
          },
          title: {
            display: true,
            text: "Taxonomy distribution (order)",
            color: this.theme.global.current.dark ? "#FFFFFF" : "#000000",
          },
          legend: { position: "right" },
        },
      };
    },
    chartData() {
      const [labels, values] = this.tax_distribution[0].map((_, colIndex) =>
        this.tax_distribution.map((row) => row[colIndex])
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
