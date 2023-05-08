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
              label="Hide Map"
              hide-details
              inset
              density="comfortable"
            />
          </v-col>
          <v-col class="py-1 my-auto" cols="auto">
            <v-btn
              @click="
                {
                  resetClickPoint();
                  shouldHideMap = false;
                  $emit('setHideMap', false);
                  $emit('setMap', null);
                  searchMode = '';
                }
              "
              color="info"
            >
              Reset
            </v-btn>
            <v-btn
              icon="mdi-help-circle-outline"
              color="info"
              variant="text"
              class="ms-2"
              target="_blank"
              href="https://github.com/burstein-lab/genomic-nlp-server/wiki"
            />
          </v-col>
        </v-row>
        <v-divider class="mx-4 my-4" />
        <v-select
          color="info"
          v-model="searchMode"
          :items="[...Object.keys(searchModeToType), 'Sequence']"
          label="Search Mode"
          density="comfortable"
          hide-details
        />
        <div v-if="searchMode">
          <DiamondSearch
            v-if="searchMode === 'Sequence'"
            @setMap="(e) => $emit('setMap', e)"
            @setLoading="(e: boolean) => loading = e"
          />
          <Search
            v-else
            :key="searchMode"
            :label="searchModeToType[searchMode].label"
            :type="searchModeToType[searchMode].type"
            @search="(e: string[]) => searchSpaces(searchModeToType[searchMode].emit, e)"
          />
        </div>
        <v-divider class="mx-4 mt-4" />
        <div v-if="hoverPoint">
          <SpaceInfo :space="hoverPoint" />
          Click point for actions
        </div>
        <div v-else-if="clickedCircle">
          <SpaceInfo :space="clickedCircle.feature.properties" />
          <v-container class="text-center pt-1 pb-0">
            <v-row justify="center" no-gutters>
              <v-col cols="1">
                <v-tooltip text="Move to point" location="bottom">
                  <template v-slot:activator="{ props }">
                    <v-btn-group density="comfortable" v-bind="props">
                      <v-btn
                        color="info"
                        icon
                        density="comfortable"
                        @click="$emit('centerPoint')"
                      >
                        <v-icon>mdi-target</v-icon>
                      </v-btn>
                    </v-btn-group>
                  </template>
                </v-tooltip>
              </v-col>
              <v-col cols="10">
                <v-btn-toggle
                  color="info"
                  variant="outlined"
                  v-model="plotToggle"
                  density="comfortable"
                  size="small"
                >
                  <v-btn value="bar" :disabled="loading" density="comfortable">
                    Neighbors
                  </v-btn>
                  <v-btn
                    value="scatter"
                    :disabled="
                      loading ||
                      !clickedCircle.feature.properties.value.hypothetical
                    "
                    density="comfortable"
                  >
                    Gene Predictions
                  </v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="1">
                <v-btn-group density="comfortable">
                  <v-btn color="grey" icon dark @click="resetClickPoint">
                    <v-icon>mdi-close</v-icon>
                  </v-btn>
                </v-btn-group>
              </v-col>
            </v-row>
          </v-container>
          <NeighborsPlot
            v-if="plotToggle == 'bar' && barData"
            :data="barData"
          />
          <PredictionPlot
            v-else-if="plotToggle == 'scatter' && scatterData"
            :data="scatterData"
          />
        </div>
        <div v-else class="pt-2">
          Search to explore the model and hover a point to view extra options
        </div>
        <div v-if="loading" class="pt-2">
          Getting data...
          <v-progress-linear indeterminate color="info" rounded />
        </div>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Search from "./Search.vue";
import ThemeToggle from "./ThemeToggle.vue";
import SpaceInfo from "./SpaceInfo.vue";
import DiamondSearch from "./DiamondSearch.vue";
import NeighborsPlot from "./NeighborsPlot.vue";
import PredictionPlot from "./PredictionPlot.vue";
import { useHoverPoint, useClickedCircle } from "@/composables/states";
import { SpacesReponse, ScatterData } from "@/composables/spaces";
import { searchSpaces } from "@/composables/spaces";

interface SearchMode {
  label: string;
  type: string;
  emit: string;
}

const searchMode = (
  label: string,
  type?: string,
  emit?: string
): SearchMode => ({
  label,
  type: type ? type : label.toLowerCase(),
  emit: emit ? emit : label.toLowerCase(),
});

export default {
  name: "ControlCard",
  components: {
    NeighborsPlot,
    PredictionPlot,
    Search,
    ThemeToggle,
    SpaceInfo,
    DiamondSearch,
  },
  data: () => {
    const controller = new AbortController();
    return {
      searchMode: "",
      searchModeToType: {
        Space: searchMode("Space"),
        Label: searchMode("Label"),
        "KO / Hypo": searchMode("KO / Hypo", "word", "word"),
        Neighbors: searchMode("Word", "word", "neighbors"),
        Gene: searchMode("Gene"),
      } as { [key: string]: SearchMode },
      neighbors: null as string[] | null,
      barData: null as SpacesReponse | null,
      controller: controller,
      loading: false,
      plotToggle: "",
      scatterData: null as ScatterData | null,
      hoverPoint: useHoverPoint(),
      clickedCircle: useClickedCircle(),
      shouldHideMap: false,
    };
  },
  emits: ["centerPoint", "resetClickPoint", "setMap", "setHideMap"],
  methods: {
    resetClickPoint() {
      this.$emit("resetClickPoint");
      this.clickedCircle = null;
    },
    async searchSpaces(type: string, e: string[]) {
      this.loading = true;
      this.$emit("setMap", await searchSpaces(type, e, this.controller.signal));
      this.loading = false;
    },
  },
  watch: {
    clickedCircle(val) {
      this.controller.abort();
      this.controller = new AbortController();
      this.loading = false;
      this.barData = null;
      this.scatterData = null;
      this.plotToggle = "";
    },
    async plotToggle(val) {
      if (val == "bar" && !this.barData) {
        this.loading = true;
        const rawRes = await fetch(
          `${import.meta.env.VITE_SERVER_URL}/neighbors/get/${
            this.clickedCircle?.feature.properties.value.word
          }?with_distance=true&k=10`,
          { signal: this.controller.signal }
        );
        const res = await rawRes.json();
        this.barData = res;
        this.loading = false;
      } else if (val == "scatter" && !this.scatterData) {
        this.loading = true;
        const rawRes = await fetch(
          `${import.meta.env.VITE_SERVER_URL}/plot/scatter/${
            this.clickedCircle?.feature.properties.value.word
          }`,
          { signal: this.controller.signal }
        );
        const res = await rawRes.json();
        this.scatterData = res;
        this.loading = false;
      }
    },
  },
};
</script>
