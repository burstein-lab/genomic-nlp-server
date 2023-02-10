<template>
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
        <Search
          v-if="searchMode === 'Space'"
          @search="(e: string[]) => onSearch('space', e)"
          label="Space"
          type="space"
        />
        <Search
          v-if="searchMode === 'Label'"
          @search="(e: string[]) => onSearch('label', e)"
          label="Label"
          type="label"
        />
        <Search
          v-if="searchMode === 'KO / Hypo'"
          @search="(e: string[]) => onSearch('word', e)"
          label="KO / Hypo"
          type="word"
          multiple
        />
        <div v-if="searchMode === 'Neighbors'">
          <Search
            @search="(e: string[]) => {neighbors=e; onSearch('neighbors', e)}"
            label="Word"
            type="word"
          />
          <v-text-field v-model="kNeighbors" label="K" type="number" />
        </div>
        <Search
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
            @click:append="onSequenceSearch(sequence)"
          />
          <v-file-input show-size v-model="sequenceFile" label="From file" />
        </div>
      </v-card-text>
    </div>
    <v-divider class="mx-4" />
    <v-card-text>
      <div v-if="hoverPoint">
        <SpaceInfo :space="hoverPoint" />
        Click point for more options
      </div>
      <div v-else-if="clickPoint">
        <SpaceInfo :space="clickPoint.properties" />
        <v-btn-toggle color="primary" variant="outlined" v-model="plotToggle">
          <v-btn value="bar">Bar Plot</v-btn>
          <v-btn value="scatter">Scatter Plot</v-btn>
        </v-btn-toggle>
        <v-btn-group>
          <v-btn color="primary" @click="centerPoint">Center</v-btn>
          <v-btn color="grey" icon dark @click="resetClickPoint">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-btn-group>
        <BarChart
          v-if="plotToggle == 'bar' && clickPoint && barData"
          :chartData="barData"
          :options="{ title: { display: false } }"
        />
        <ScatterChart
          v-if="plotToggle == 'scatter' && clickPoint && scatterData"
          :chartData="scatterData"
          :options="scatterOptions"
        />
      </div>
      <div v-else>
        Search to explore the model and hover a point to view extra options
      </div>
      <div v-if="loading">
        Getting data...
        <v-progress-linear indeterminate color="primary" rounded />
      </div>
    </v-card-text>
  </v-card>
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

export default {
  name: "ControlCard",
  components: { Search, BarChart, ScatterChart, ThemeToggle, SpaceInfo },
  props: {},
  data: () => {
    return {
      searchMode: "",
      neighbors: null as string[] | null,
      barData: null as Object | null,
      loading: false,
      plotToggle: "",
      scatterData: null as Object | null,
      scatterOptions: null as Object | null,
      sequenceFile: new Array(),
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
    onSequenceSearch(sequence: string) {
      this.loading = true;
      this.$emit("sequenceSearch", sequence);
      // TODO: do search here so loading will behave well.
      this.loading = false;
    },
    onSearch(type: string, e: string[]) {
      this.loading = true;
      this.$emit("search", type, e, this.kNeighbors);
      // TODO: do search here so loading will behave well.
      this.loading = false;
    },
    centerPoint() {
      this.$emit("centerPoint");
    },
    loadTextFromFile(ev) {
      const file = ev.target.files[0];
      const reader = new FileReader();

      reader.onload = (e) => this.$emit("load", e.target.result);
      reader.readAsText(file);
    },
  },
  watch: {
    sequenceFile(val) {
      if (!val) {
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        this.onSequenceSearch(e.target.result);
      };
      reader.readAsText(val[0]);
    },
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
    clickPoint(val) {
      this.barData = null;
      this.scatterData = null;
      this.scatterOptions = null;
      this.plotToggle = "";
    },
    plotToggle(val) {
      if (val == "bar") {
        this.loading = true;
        fetch(
          `${this.apiUrl}/plot/bar/${this.clickPoint?.properties.value.word}`
        )
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
            this.loading = false;
          })
          .catch((err) => {
            console.error(err);
          });
      } else if (val == "scatter") {
        this.loading = true;
        fetch(
          `${this.apiUrl}/plot/scatter/${this.clickPoint?.properties.value.word}`
        )
          .then((res) => res.json())
          .then((res) => {
            this.scatterOptions = {
              scales: {
                x: {
                  ticks: {
                    // Include a dollar sign in the ticks
                    callback: (value: string, index: number, ticks: any[]) => {
                      return res.ticks[index];
                    },
                  },
                },
              },
            };
            this.scatterData = {
              // plt.yscale('log')
              //plt.ylabel('Prediction Score')
              datasets: [
                {
                  label: res.label,
                  data: res.data,
                  backgroundColor: "#da4ca4",
                },
              ],
            };
            this.loading = false;
          })
          .catch((err) => {
            console.error(err);
          });
      }
    },
  },
};
</script>
