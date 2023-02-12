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
          <v-btn
            v-if="downloadableDiamondResult"
            @click="downloadDiamondResult"
          >
            Download diamond result
          </v-btn>
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
          <v-btn value="scatter">Gene Predictions</v-btn>
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
import { spacesToCollection, Coords, LatLng } from "@/composables/spaces";

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
      diamondUrl: new URL(`${import.meta.env.VITE_DIAMOND_URL}`),
      serverUrl: new URL(import.meta.env.VITE_SERVER_URL),
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
      downloadableDiamondResult: "",
    };
  },
  emits: ["centerPoint", "resetClickPoint", "setMap"],
  methods: {
    resetClickPoint() {
      this.$emit("resetClickPoint");
      this.clickPoint = null;
    },
    async onSearch(type: string, e: string[]) {
      const url = new URL(`${this.apiUrl}/${type}/get/${e.toString()}`);
      if (type === "neighbors") {
        url.searchParams.append("k", this.kNeighbors.toString());
      }
      const rawRes = await fetch(url.href);
      const res = await rawRes.json();
      this.$emit(
        "setMap",
        res.latlng,
        res.zoom,
        spacesToCollection(
          res.spaces,
          {
            z: res.zoom,
            x: res.latlng.lng,
            y: res.latlng.lat,
          },
          true
        )
      );

      return res.spaces;
    },
    downloadDiamondResult() {
      // credit: https://www.bitdegree.org/learn/javascript-download
      let filename = "file.tsv";
      let element = document.createElement("a");
      element.setAttribute(
        "href",
        "data:application/json;charset=utf-8," +
          encodeURIComponent(this.downloadableDiamondResult)
      );
      element.setAttribute("download", filename);

      element.style.display = "none";
      document.body.appendChild(element);

      element.click();
      document.body.removeChild(element);
    },
    centerPoint() {
      this.$emit("centerPoint");
    },
    async onSequenceSearch(sequence: string) {
      this.loading = true;
      const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sequence }),
      };
      const url = new URL(`${this.diamondUrl}diamond`);
      const rawRes = await fetch(url.href, requestOptions);
      const res = await rawRes.json();
      // for each line in the output, split on tab and take the second element.
      const out = res["out"].trim().split("\n");
      const ids = out.map((line: string) => line.split("\t")[1]);
      const searchResult = await this.onSearch("word", ids, 0);
      if (!searchResult) return;
      let result =
        "query\tword\tcolumn_1\tcolumn_2\tko\tlabel\tproduct\tgene_name\tsignificant\tpredicted_class\n";

      for (let i = 0; i < searchResult.length; i++) {
        result +=
          out[i] +
          "\t" +
          (searchResult[i].value.ko +
            "\t" +
            searchResult[i].value.label +
            "\t" +
            searchResult[i].value.product +
            "\t" +
            searchResult[i].value.gene_name +
            "\t" +
            searchResult[i].value.significant +
            "\t" +
            searchResult[i].value.predicted_class);
      }

      this.downloadableDiamondResult = result;
      this.loading = false;
    },
  },
  async beforeMount() {
    // ping servers to avoid cold starts.
    fetch(this.diamondUrl.href);
    fetch(this.serverUrl.href);
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
