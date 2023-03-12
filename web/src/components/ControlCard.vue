<template>
  <v-card
    width="500"
    max-height="100vh"
    style="opacity: 0.9"
    @wheel.stop
    class="overflow-y-auto"
  >
    <v-card-text>
      <v-row>
        <v-col cols="auto">
          <ThemeToggle />
        </v-col>
        <v-col cols="auto">
          <v-switch
            v-model="shouldShowMap"
            @update:modelValue="$emit('setMapVisibility', shouldShowMap)"
            color="primary"
            label="Show Map"
            hide-details
          />
        </v-col>
        <v-col></v-col>
        <v-col class="my-auto" cols="auto">
          <v-btn
            @click="
              {
                $emit('setMapVisibility', true);
                $emit('setMap', null);
                resetClickPoint();
                searchMode = '';
              }
            "
          >
            Reset
          </v-btn>
          <v-btn
            icon="mdi-help-circle-outline"
            variant="text"
            class="ms-2"
            href="https://github.com/burstein-lab/genomic-nlp-server/wiki"
          />
        </v-col>
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
          @search="(e: string[]) => searchSpaces('space', e)"
          label="Space"
          type="space"
        />
        <Search
          v-if="searchMode === 'Label'"
          @search="(e: string[]) => searchSpaces('label', e)"
          label="Label"
          type="label"
        />
        <Search
          v-if="searchMode === 'KO / Hypo'"
          @search="(e: string[]) => searchSpaces('word', e)"
          label="KO / Hypo"
          type="word"
          multiple
        />
        <div v-if="searchMode === 'Neighbors'">
          <Search
            @search="(e: string[]) => {neighbors=e; searchSpaces('neighbors', e, kNeighbors)}"
            label="Word"
            type="word"
          />
          <v-text-field v-model="kNeighbors" label="K" type="number" />
        </div>
        <Search
          v-if="searchMode === 'Gene'"
          @search="(e: string[]) => searchSpaces('gene', e)"
          label="Gene"
          type="gene"
        />
        <div v-if="searchMode === 'Sequence'">
          <DiamondSearch
            @setMap="(e) => $emit('setMap', e)"
            @setLoading="(e: boolean) => loading = e"
          />
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
          <v-btn value="bar">Closest Neighbors</v-btn>
          <v-btn
            :disabled="!clickPoint?.properties.value.hypothetical"
            value="scatter"
          >
            <div>Gene Predictions</div>
          </v-btn>
        </v-btn-toggle>
        <v-btn-group>
          <v-btn color="primary" @click="$emit('centerPoint')">Center</v-btn>
          <v-btn color="grey" icon dark @click="resetClickPoint">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-btn-group>
        <BarChart
          v-if="plotToggle == 'bar' && clickPoint && barData"
          class="mt-3"
          :chartData="barData"
          :options="{
            title: { display: false },
            scales: { y: { title: { display: true, text: 'Similarity' } } },
            plugins: { legend: { display: false } },
          }"
        />
        <ScatterChart
          v-if="plotToggle == 'scatter' && clickPoint && scatterData"
          class="mt-3"
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
import DiamondSearch from "./DiamondSearch.vue";
import { useHoverPoint, useClickPoint } from "../composables/states";
import { searchSpaces } from "@/composables/spaces";

import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

export default {
  name: "ControlCard",
  components: {
    Search,
    BarChart,
    ScatterChart,
    ThemeToggle,
    SpaceInfo,
    DiamondSearch,
  },
  data: () => {
    return {
      searchMode: "",
      neighbors: null as string[] | null,
      barData: null as Object | null,
      loading: false,
      plotToggle: "",
      scatterData: null as Object | null,
      scatterOptions: null as Object | null,
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
      shouldShowMap: true,
      apiUrl: import.meta.env.VITE_SERVER_URL,
    };
  },
  emits: ["centerPoint", "resetClickPoint", "setMap", "setMapVisibility"],
  methods: {
    resetClickPoint() {
      this.$emit("resetClickPoint");
      this.clickPoint = null;
    },
    async searchSpaces(type: string, e: string[], k?: number) {
      this.loading = true;
      this.$emit("setMap", await searchSpaces(type, e, k));
      this.loading = false;
    },
  },
  async beforeMount() {
    // ping servers to avoid cold starts.
    fetch(new URL(`${import.meta.env.VITE_DIAMOND_URL}`).href);
    fetch(new URL(this.apiUrl).href);
  },
  watch: {
    searchMode(val: string) {
      this.kNeighbors = 20;
    },
    async kNeighbors(val: number) {
      if (val < 1) {
        this.kNeighbors = 1;
      } else if (val > 100) {
        this.kNeighbors = 100;
      }
      if (this.neighbors !== null) {
        this.searchSpaces("neighbors", this.neighbors, this.kNeighbors);
      }
    },
    clickPoint(val) {
      this.barData = null;
      this.scatterData = null;
      this.scatterOptions = null;
      this.plotToggle = "";
    },
    async plotToggle(val) {
      if (val == "bar") {
        this.loading = true;
        const rawRes = await fetch(
          `${this.apiUrl}/plot/bar/${this.clickPoint?.properties.value.word}`
        );
        const res = await rawRes.json();
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
      } else if (val == "scatter") {
        this.loading = true;
        const rawRes = await fetch(
          `${this.apiUrl}/plot/scatter/${this.clickPoint?.properties.value.word}`
        );
        const res = await rawRes.json();
        this.scatterOptions = {
          scales: {
            x: {
              title: {
                display: true,
                text: "Predicted functional category",
              },
              ticks: {
                callback: (value: string, index: number, ticks: any[]) => {
                  return res.ticks[index];
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
                  if (value === 0) return "0";
                  return "1e" + value;
                },
              },
            },
          },
        };
        this.scatterData = {
          datasets: [
            {
              label: res.label,
              data: res.data,
              backgroundColor: "#da4ca4",
            },
          ],
        };
        this.loading = false;
      }
    },
  },
};
</script>
