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
      ],
    };
  },
  methods: {
    options() {
      return {
        plugins: {
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
          legend: {
            position: "right",
            labels: {
              color: this.theme.global.current.dark ? "#FFFFFF" : "#000000",
            },
          },
        },
      };
    },
    chartData() {
      const pairs = this.tax_distribution.filter(([_, number]) => number);
      console.log(pairs, this.tax_distribution);
      const [labels, values] = pairs[0].map((_, colIndex) =>
        pairs.map((row) => row[colIndex])
      );

      const palette = [...this.palette];

      const positionOfOther = labels.indexOf("Other");
      if (positionOfOther !== -1) {
        palette.splice(positionOfOther, 0, "#808080");
      }

      return {
        labels: labels,
        datasets: [
          {
            data: values,
            backgroundColor: palette,
            borderColor: this.theme.global.current.dark ? "#202020" : "#FFFFFF",
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
