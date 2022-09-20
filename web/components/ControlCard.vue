<template>
  <div>
    <v-card width="500" color="rgba(255, 255, 255, 0.8)">
      <v-card-text>
        <v-switch
          v-model="shouldShowMap"
          color="primary"
          label="Show Map"
          hide-details
        />
        <v-select
          v-model="searchMode"
          :items="searchModes"
          label="Search Mode"
        />
        <search
          v-if="searchMode === 'Space'"
          @select="(e: string[]) => onSelect('space', e)"
          label="Space"
          type="space"
        />
        <search
          v-if="searchMode === 'Label'"
          @select="(e: string[]) => onSelect('label', e)"
          label="Label"
          type="label"
        />
        <search
          v-if="searchMode === 'KO / Hypo'"
          @select="(e: string[]) => onSelect('word', e)"
          label="KO / Hypo"
          type="word"
          multiple
        />
        <div v-if="searchMode === 'Neighbors'">
          <search
            @select="(e: string[]) => {neighbors=e; onSelect('neighbors', e)}"
            label="Word"
            type="word"
          />
          <v-text-field v-model="kNeighbors" label="K" type="number" />
        </div>
        <search
          v-if="searchMode === 'Gene'"
          @select="(e: string[]) => onSelect('gene', e)"
          label="Gene"
          type="gene"
        />
      </v-card-text>
      <v-divider class="mx-4" />
      <v-card-text>
        <div v-if="loading">
          Getting data...
          <v-progress-linear indeterminate color="primary" rounded />
        </div>
        <div v-else-if="hoverPoint">
          {{ hoverPoint }}
          Click point for more options
        </div>
        <div v-else-if="clickPoint">
          {{ clickPoint }}
          <v-btn color="primary" @click="barPlot">Bar Plot</v-btn>
          <v-btn color="primary" @click="scatterPlot">Scatter Plot</v-btn>
          <v-btn class="ma-1" color="grey" icon dark @click="clickPoint = null">
            <v-icon>mdi-close</v-icon>
          </v-btn>
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
export default {
  components: { BarChart, ScatterChart },
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    searchMode: null,
    neighbors: null,
    barData: null,
    hoverPoint: useHoverPoint(),
    clickPoint: useClickPoint(),
    kNeighbors: 20,
    searchModes: ["Space", "Label", "KO / Hypo", "Neighbors", "Gene"],
    shouldShowMap: useShouldShowMap(),
    apiUrl: "http://127.0.0.1:5000/",
  }),
  methods: {
    onSelect(type: string, e: string[]) {
      this.$emit("select", type, e, this.kNeighbors);
    },
    barPlot() {
      fetch(`${this.apiUrl}/plot/bar/${this.clickPoint.value.word}`)
        .then((res) => res.json())
        .then((res) => {
          this.barData = {
            labels: res.x,
            datasets: [
              {
                data: res.y,
              },
            ],
          };
        })
        .catch((err) => {
          console.error(err);
        });
    },
    scatterPlot() {
      fetch(`${this.apiUrl}/plot/scatter/${this.clickPoint.value.word}`)
        .then((res) => res.json())
        .then((res) => {
          this.barData = {
            labels: res.x,
            datasets: [
              {
                data: res.y,
              },
            ],
          };
        })
        .catch((err) => {
          console.error(err);
        });
    },
  },
  watch: {
    kNeighbors(val: number) {
      if (val < 1) {
        this.kNeighbors = 1;
        return;
      } else if (val > 100) {
        this.kNeighbors = 100;
        return;
      }
      // TODO(#85): doesn't change when mode changes but the input is reset.
      if (this.neighbors !== null) {
        this.onSelect("neighbors", this.neighbors);
      }
    },
    clickPoint(val: Point) {
      this.barData = null;
    },
  },
};
</script>
