<template>
  <v-card
    width="500"
    max-height="100vh"
    style="opacity: 0.9"
    @wheel.stop
    class="overflow-y-auto"
  >
    <v-card-text>
      <v-container class="pa-0">
        <v-row>
          <v-col class="py-1" cols="auto">
            <ThemeToggle />
          </v-col>
          <v-col class="py-1" cols="auto">
            <v-switch
              v-model="shouldHideMap"
              @update:modelValue="$emit('setHideMap', shouldHideMap)"
              color="info"
              label="Hide map"
              hide-details
              inset
              density="comfortable"
            />
          </v-col>
          <v-col class="py-1 my-auto" cols="auto">
            <v-btn @click="reload" color="info"> Reset </v-btn>
            <v-btn
              icon="mdi-help-circle-outline"
              color="info"
              variant="text"
              class="ms-2"
              target="_blank"
              href="https://github.com/burstein-lab/genomic-nlp-server#dna-genlp"
            />
          </v-col>
        </v-row>
        <v-divider class="mx-4 my-4" />
        <v-select
          color="info"
          v-model="searchMode"
          @update:modelValue="updateSearchMode"
          :items="searchModes"
          label="Search mode"
          density="comfortable"
          hide-details
        />
        <div>
          <Search
            :key="searchMode"
            :searchMode="searchMode"
            @search="(emit: string, e: string[]) => searchSpaces(emit, e)"
          />
          <!-- <DiamondSearch
            v-else
            :isLoading="isDiamondLoading"
            @setMap="(e) => $emit('setMap', e)"
            @setLoading="(isLoading: boolean) => {$emit('setDiamondLoading', isLoading);}"
          /> -->
        </div>
        <v-divider class="mx-4 mt-4" />
        <div v-if="hoveredSpace">
          <SpaceInfo
            :space="hoveredSpace"
            :actionable="false"
            :backable="false"
          />
          Click point for actions
        </div>
        <div v-else-if="clickedSpace">
          <SpaceInfo
            :space="clickedSpace"
            :actionable="true"
            :backable="previousPoint != null"
            @downloadSequence="downloadSequence"
            @centerPoint="$emit('centerPoint')"
            @resetClickPoint="resetClickPoint"
            @back="onBack"
          />
          <v-container class="text-center pt-1 py-0">
            <v-row justify="center" no-gutters>
              <v-col cols="11">
                <v-btn-toggle
                  color="info"
                  variant="outlined"
                  v-model="plotToggle"
                  density="comfortable"
                  size="small"
                >
                  <v-btn
                    value="neighbors"
                    :disabled="isLoading"
                    density="comfortable"
                  >
                    Neighbors
                  </v-btn>
                  <v-btn
                    value="predictions"
                    :disabled="isLoading || !clickedSpace.value.hypothetical"
                    density="comfortable"
                  >
                    Func Pred
                  </v-btn>
                  <v-btn
                    value="taxMap"
                    :disabled="
                      isLoading || !clickedSpace.value.tax_distribution
                    "
                    density="comfortable"
                  >
                    Tax Map
                  </v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="1">
                <v-tooltip text="Download graph data" location="bottom">
                  <template v-slot:activator="{ props }">
                    <v-btn-group density="comfortable" v-bind="props">
                      <v-btn
                        color="info"
                        icon
                        :disabled="
                          !(
                            (plotToggle === 'neighbors' && barData) ||
                            (plotToggle === 'predictions' && scatterData)
                          )
                        "
                        density="comfortable"
                        @click="downloadGraphData"
                      >
                        <v-icon>mdi-download</v-icon>
                      </v-btn>
                    </v-btn-group>
                  </template>
                </v-tooltip>
              </v-col>
            </v-row>
          </v-container>
          <NeighborsPlot
            v-if="plotToggle == 'neighbors' && barData"
            @click="(e) => onNeighborsClick(e)"
            :data="barData"
          />
          <PredictionPlot
            v-else-if="plotToggle == 'predictions' && scatterData"
            :data="scatterData"
          />
          <TaxMapPlot
            v-else-if="plotToggle == 'taxMap'"
            :tax_distribution="clickedSpace.value.tax_distribution"
            :tax_ratio="clickedSpace.value.tax_ratio"
          />
        </div>
        <div v-else class="pt-2">
          Search to explore the model and hover a point to view extra options
        </div>
        <div v-if="isLoading" class="pt-2">
          {{
            isDiamondLoading
              ? "Searching similar sequences, please wait..."
              : "Getting data..."
          }}
          <v-progress-linear indeterminate color="info" rounded />
        </div>
      </v-container>
    </v-card-text>
  </v-card>
  <Snackbar :show="snackbar" @close="snackbar = false" />
</template>

<script lang="ts">
import Search from "./Search.vue";
import ThemeToggle from "./ThemeToggle.vue";
import SpaceInfo from "./SpaceInfo.vue";
import DiamondSearch from "./DiamondSearch.vue";
import NeighborsPlot from "./NeighborsPlot.vue";
import PredictionPlot from "./PredictionPlot.vue";
import TaxMapPlot from "./TaxMapPlot.vue";
import Snackbar from "./Snackbar.vue";
import { SpacesReponse, ScatterData } from "@/composables/spaces";
import { downloadFile } from "@/composables/utils";
import {
  searchSpaces,
  searchModeToType,
  Space,
  SpaceValue,
} from "@/composables/spaces";

export default {
  name: "ControlCard",
  components: {
    NeighborsPlot,
    PredictionPlot,
    TaxMapPlot,
    Search,
    ThemeToggle,
    SpaceInfo,
    DiamondSearch,
    Snackbar,
  },
  props: {
    hoveredSpace: {
      type: Object as () => Space | null,
    },
    clickedSpace: {
      type: Object as () => Space | null,
    },
    isDiamondLoading: {
      type: Boolean,
    },
  },
  data: () => {
    const searchModes = [...Object.keys(searchModeToType)];
    searchModes.splice(1, 0, "Sequence");
    return {
      searchMode: "",
      searchModes: searchModes,
      searchModeToType,
      neighbors: null as string[] | null,
      barData: null as SpacesReponse | null,
      controller: new AbortController(),
      loading: false,
      currentPlot: "",
      scatterData: null as ScatterData | null,
      taxData: null as Object | null,
      shouldHideMap: false,
      snackbar: false,
      previousPoint: null as Space | null,
    };
  },
  async beforeMount() {
    this.searchMode = this.$route.query.searchMode
      ? this.$route.query.searchMode
      : "KEGG ortholog";
    console.log("controlcard beforeMount searchMode", this.searchMode);
  },
  emits: [
    "setDiamondLoading",
    "centerPoint",
    "setClickPoint",
    "resetClickPoint",
    "resetCoords",
    "setMap",
    "setHideMap",
  ],
  methods: {
    reload() {
      const currentRoute = this.$router.currentRoute.value;
      const { path, name, params } = currentRoute;
      this.$router.push({ path, name, params, query: {} }).then(() => {
        // Force reload the current route
        this.$router.go(0);
      });
    },
    resetClickPoint() {
      this.$emit("resetClickPoint");
    },
    async downloadSequence() {
      const rawRes = await fetch(
        `${import.meta.env.VITE_PUBLIC_URL}fasta_per_word/${
          this.clickedSpace?.value?.word
        }.faa`,
        { signal: this.controller.signal }
      );
      downloadFile(
        `${this.clickedSpace?.value?.word}.faa`,
        await rawRes.text(),
        "text"
      );
    },
    async onNeighborsClick(word: string) {
      this.loading = true;
      this.$emit("setClickPoint", word);
      this.loading = false;
    },
    async onBack() {
      this.loading = true;
      this.$emit("setClickPoint", this.previousPoint);
      this.loading = false;
    },
    async searchSpaces(type: string, e: string | string[]) {
      this.loading = true;
      this.$router.push({
        query: {
          ...this.$route.query,
          searchValue: e.toString(),
        },
      });
      this.$emit("setMap", await searchSpaces(type, e, this.controller.signal));
      this.loading = false;
    },
    async updateSearchMode(val: string) {
      this.resetClickPoint();
      if (val === "Neighbors") this.snackbar = true;
      await this.$router.push({
        query: {
          ...this.$route.query,
          searchMode: val,
        },
      });
      this.searchMode = val;
    },
    downloadGraphData() {
      if (this.plotToggle == "neighbors") {
        downloadFile(
          this.$route.query.clickedSpace + ".neighbors.tsv",
          this.neighborsToTSV(
            this.barData.spaces.map((space: Space) => space.value)
          )
        );

        return;
      }

      downloadFile(
        this.$route.query.clickedSpace + ".prediction.tsv",
        this.predictionToTSV(
          this.scatterData.ticks,
          this.scatterData.data.map((v: { x: Number; y: Number }) => v.y)
        )
      );
    },
    predictionToTSV(ticks: string[], values: Number[]) {
      const res = ["Functional category\tPrediction score (1e)"];
      for (let i = 0; i < ticks.length; i++) {
        res.push(ticks[i] + "\t" + values[i]);
      }

      return res.join("\n");
    },
    neighborsToTSV(spaces: SpaceValue[]) {
      const header: string[] = [
        "Word",
        "KEGG Orthology",
        "Product",
        "Gene name",
        "Functional category",
        "Prediction confidence",
        "NCBI NR description",
        "Distance",
        "Gene count in family",
      ];
      const result: Object[] = [];

      spaces.forEach((space) => {
        result.push({
          Word: space.word,
          "KEGG Orthology": space.ko,
          Product: space.product,
          "Gene name": space.gene_name,
          "Functional category":
            space.predicted_class + (space.hypothetical ? " [PREDICTED]" : ""),
          "Prediction confidence": space.hypothetical
            ? space.significant
              ? "high"
              : "low"
            : "N/A",
          "NCBI NR description": space.hypothetical ? space.ncbi_nr : "N/A",
          Distance: space.distance,
          "Gene count in family": space.word_count,
        });
      });

      return (
        header.join("\t") +
        "\n" +
        result.map((row) => Object.values(row).join("\t")).join("\n")
      );
    },
  },
  computed: {
    isLoading(): boolean {
      return this.loading || this.isDiamondLoading;
    },
    plotToggle: {
      get() {
        return this.currentPlot;
      },
      async set(val: string) {
        this.currentPlot = val;
        // await this.$router.push({
        //   query: {
        //     ...this.$route.query,
        //     clickedSpace: this.clickedSpace?.value?.word
        //       ? this.clickedSpace?.value?.word
        //       : "",
        //     plot: val,
        //   },
        // });
        if (val == "neighbors" && !this.barData) {
          this.loading = true;
          this.snackbar = true;
          const rawRes = await fetch(
            `${import.meta.env.VITE_SERVER_URL}/neighbors/get/${
              this.clickedSpace.value.word
            }?with_distance=true&k=10`,
            { signal: this.controller.signal }
          );
          this.barData = await rawRes.json();
          this.loading = false;
        } else if (val == "predictions" && !this.scatterData) {
          this.loading = true;
          const rawRes = await fetch(
            `${import.meta.env.VITE_SERVER_URL}/plot/scatter/${
              this.clickedSpace.value.word
            }`,
            { signal: this.controller.signal }
          );
          this.scatterData = await rawRes.json();
          this.loading = false;
        }
      },
    },
  },
  watch: {
    clickedSpace(newVal, oldVal) {
      console.log("controlcard clickedSpace", newVal, oldVal);
      if (oldVal === undefined && newVal && this.$route.query.plot) {
        // Only happens on first load. After that, oldVal is either set, or null.
        this.plotToggle = this.$route.query.plot;
        return;
      }

      if (oldVal && newVal && oldVal.value.word !== newVal.value.word) {
        this.previousPoint = oldVal?.value?.word;
      } else {
        this.previousPoint = null;
      }

      this.controller.abort();
      this.controller = new AbortController();
      this.barData = null;
      this.scatterData = null;
      this.plotToggle = "";
    },
  },
};
</script>
