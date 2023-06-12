<template>
  <BarChart class="mt-3" :chartData="chartData()" :options="options()" />
  <v-container class="ps-0 pe-0 pb-0">
    <v-row>
      <v-col>
        <v-btn @click="downloadGraphData" color="info">
          Download Graph Data
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { BarChart } from "vue-chart-3";
import {
  spaceToInfo,
  SpaceValue,
  Space,
  SpacesReponse,
} from "@/composables/spaces";
import { downloadFile } from "@/composables/utils";

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
  emits: ["click"],
  methods: {
    hover(item: any) {
      const infoMap = spaceToInfo(this.data.spaces[item.dataIndex].value);
      return Array.from(infoMap, ([key, value]) => `${key}: ${value}`);
    },
    downloadGraphData() {
      downloadFile(
        "graph_data.tsv",
        this.spacesToTSV(this.data.spaces.map((space: Space) => space.value))
      );
    },
    spacesToTSV(spaces: SpaceValue[]) {
      const header: string[] = [
        "Word",
        "KO",
        "Product",
        "Gene name",
        "Functional category",
        "Prediction confidence",
        "Distance",
      ];
      const result: Object[] = [];

      spaces.forEach((space) => {
        result.push({
          Word: space.word,
          KO: space.ko,
          Product: space.product,
          "Gene name": space.gene_name,
          "Functional category":
            space.predicted_class + (space.hypothetical ? " [PREDICTED]" : ""),
          "Prediction confidence": space.hypothetical
            ? space.significant
              ? "high"
              : "low"
            : "N/A",
          Distance: space.distance,
        });
      });

      return (
        header.join("\t") +
        "\n" +
        result.map((row) => Object.values(row).join("\t")).join("\n")
      );
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
