<template>
  <div>
    <v-card width="500" style="opacity: 0.9">
      <v-card-text>
        <v-row>
          <v-col cols="auto">
            <ThemeToggle />
          </v-col>
          <v-col cols="auto">
            <v-switch
              v-model="shouldShowMap"
              color="primary"
              label="Show Map"
              hide-details
            />
          </v-col>
          <v-col></v-col>
        </v-row>
      </v-card-text>
      <v-divider class="mx-4 mb-4" />
      <v-card-text>
        <v-select
          color="primary"
          v-model="searchMode"
          :items="searchModes"
          label="Search Mode"
        />
      </v-card-text>
      <div v-if="searchMode">
        <v-divider class="mx-4 mb-4" />
        <v-card-text>
          <search
            v-if="searchMode === 'Space'"
            @search="(e: string[]) => onSearch('space', e)"
            label="Space"
            type="space"
          />
          <search
            v-if="searchMode === 'Label'"
            @search="(e: string[]) => onSearch('label', e)"
            label="Label"
            type="label"
          />
          <search
            v-if="searchMode === 'KO / Hypo'"
            @search="(e: string[]) => onSearch('word', e)"
            label="KO / Hypo"
            type="word"
            multiple
          />
          <div v-if="searchMode === 'Neighbors'">
            <search
              @search="(e: string[]) => {neighbors=e; onSearch('neighbors', e)}"
              label="Word"
              type="word"
            />
            <v-text-field v-model="kNeighbors" label="K" type="number" />
          </div>
          <search
            v-if="searchMode === 'Gene'"
            @search="(e: string[]) => onSearch('gene', e)"
            label="Gene"
            type="gene"
          />
          <div v-if="searchMode === 'Sequence'">
            <v-textarea
              v-model="sequence"
              filled
              auto-grow
              label="Search by sequence"
              rows="4"
              row-height="30"
              shaped
              append-icon="mdi-send"
              @click:append="onSequenceSearch('sequence', [sequence])"
            />
            <v-file-input show-size label="From file" />
          </div>
        </v-card-text>
      </div>
      <v-divider class="mx-4" />
      <v-card-text>
        <div v-if="loading">
          Getting data...
          <v-progress-linear indeterminate color="primary" rounded />
        </div>
        <div v-else-if="hoverPoint">
          <SpaceInfo :space="hoverPoint" />
          Click point for more options
        </div>
        <div v-else-if="clickPoint">
          <SpaceInfo :space="clickPoint.properties" />
          <v-btn-group>
            <v-btn color="primary" @click="centerPoint">Center</v-btn>
            <v-btn color="primary" @click="barPlot">Bar Plot</v-btn>
            <v-btn color="primary" @click="scatterPlot">Scatter Plot</v-btn>
            <v-btn color="grey" icon dark @click="resetClickPoint">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-btn-group>
          <div v-if="clickPoint && barData">
            <BarChart :chartData="barData" />
          </div>
          <div v-if="clickPoint && scatterData">
            <ScatterChart :chartData="scatterData" />
          </div>
        </div>
        <div v-else>
          Search to explore the model and hover a point to view extra options
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
import { BarChart, ScatterChart } from "vue-chart-3";
import Search from "./Search.vue";
import ThemeToggle from "./ThemeToggle.vue";
import SpaceInfo from "./SpaceInfo.vue";
import {
  useHoverPoint,
  useClickPoint,
  useShouldShowMap,
} from "../composables/states";

import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

// import { Chart, DoughnutController, ArcElement, Tooltip } from 'chart.js';
// Chart.register(DoughnutController, ArcElement, Tooltip);

// import {
//   Chart as ChartJS,
//   Title,
//   Tooltip,
//   Legend,
//   BarElement,
//   CategoryScale,
//   LinearScale
// } from 'chart.js'
// ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default {
  name: "ControlCard",
  components: { Search, BarChart, ScatterChart, ThemeToggle, SpaceInfo },
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data: () => {
    return {
      searchMode: null,
      neighbors: null,
      barData: null,
      scatterData: null,
      hoverPoint: useHoverPoint(),
      clickPoint: useClickPoint(),
      kNeighbors: 20,
      searchModes: [
        "Space",
        "Label",
        "KO / Hypo",
        "Neighbors",
        "Gene",
        "Sequence",
      ],
      sequence: "",
      shouldShowMap: useShouldShowMap(),
      apiUrl: import.meta.env.VITE_SERVER_URL,
    };
  },
  emits: ["search", "sequenceSearch", "centerPoint", "resetClickPoint"],
  methods: {
    resetClickPoint() {
      this.$emit("resetClickPoint");
      this.clickPoint = null;
    },
    onSequenceSearch() {
      this.$emit("sequenceSearch", this.sequence);
    },
    onSearch(type: string, e: string[]) {
      this.$emit("search", type, e, this.kNeighbors);
    },
    centerPoint() {
      this.$emit("centerPoint");
    },
    barPlot() {
      console.log("point", this.clickPoint);
      console.log("props", this.clickPoint.properties);
      fetch(`${this.apiUrl}/plot/bar/${this.clickPoint.properties.value.word}`)
        .then((res) => res.json())
        .then((res) => {
          this.barData = {
            labels: res.x,
            datasets: [
              {
                data: res.y,
                backgroundColor: "#da4ca4",
              },
            ],
          };
        })
        .catch((err) => {
          console.error(err);
        });
    },
    scatterPlot() {
      fetch(
        `${this.apiUrl}/plot/scatter/${this.clickPoint.properties.value.word}`
      )
        .then((res) => res.json())
        .then((res) => {
          this.scatterData = {
            // plt.yscale('log')
            //plt.ylabel('Prediction Score')
            datasets: [res],
          };
        })
        .catch((err) => {
          console.error(err);
        });
    },
  },
  watch: {
    searchMode(val: string) {
      this.kNeighbors = 20;
    },
    kNeighbors(val: number) {
      if (val < 1) {
        this.kNeighbors = 1;
      } else if (val > 100) {
        this.kNeighbors = 100;
      }
      if (this.neighbors !== null) {
        this.onSearch("neighbors", this.neighbors);
      }
    },
    clickPoint(val: Point) {
      this.barData = null;
      this.scatterData = null;
    },
  },
};
</script>
