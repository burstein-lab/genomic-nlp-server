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
                resetClickPoint();
                shouldShowMap = true;
                $emit('setMapVisibility', true);
                $emit('setMap', null);
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
            target="_blank"
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
        :items="[...Object.keys(searchModeToType), 'Sequence']"
        label="Search Mode"
      />
    </v-card-text>
    <div v-if="searchMode">
      <v-divider class="mx-4 mb-4" />
      <v-card-text>
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
      </v-card-text>
    </div>
    <v-divider class="mx-4" />
    <v-card-text>
      <div v-if="hoverPoint">
        <SpaceInfo :space="hoverPoint" />
        Click point for actions
      </div>
      <div v-else-if="clickedCircle">
        <SpaceInfo :space="clickedCircle.feature.properties" />
        <v-container class="text-center">
          <v-row justify="center" no-gutters>
            <v-col cols="1">
              <v-btn-group density="comfortable">
                <v-btn
                  color="primary"
                  icon
                  density="comfortable"
                  @click="$emit('centerPoint')"
                >
                  <v-icon>mdi-target</v-icon>
                </v-btn>
              </v-btn-group>
            </v-col>
            <v-col cols="10">
              <v-btn-toggle
                color="primary"
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
        <NeighborsPlot v-if="plotToggle == 'bar' && barData" :data="barData" />
        <PredictionPlot
          v-else-if="plotToggle == 'scatter' && scatterData"
          :data="scatterData"
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
      shouldShowMap: true,
    };
  },
  emits: ["centerPoint", "resetClickPoint", "setMap", "setMapVisibility"],
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
