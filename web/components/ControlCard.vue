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
            @select="(e: string[]) => onSelect('neighbors', e)"
            label="Word"
            type="word"
          />
          <v-text-field v-model="kNeighbors" label="K" type="number" />
        </div>
      </v-card-text>
      <v-divider class="mx-4" />
      <v-card-text>
        <div v-if="loading">
          Getting data...
          <v-progress-linear indeterminate color="primary" rounded />
        </div>
        <div v-else-if="info" v-html="info" />
        <div v-else>Search to explore the model</div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
export default {
  props: {
    info: {
      type: String,
      default: "",
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    searchMode: null,
    kNeighbors: 20,
    searchModes: ["Space", "Label", "KO / Hypo", "Neighbors"],
    shouldShowMap: useShouldShowMap(),
  }),
  methods: {
    onSelect(type: string, e: string[]) {
      this.$emit("select", type, e, this.kNeighbors);
    },
  },
  watch: {
    kNeighbors(val: number) {
      if (val < 1) {
        this.kNeighbors = 1;
      } else if (val > 100) {
        this.kNeighbors = 100;
      }
    },
  },
};
</script>
