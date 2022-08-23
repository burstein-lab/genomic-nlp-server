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
        <search
          v-if="searchMode === 'Neighbors'"
          @select="(e: string[]) => onSelect('neighbors', e)"
          label="Neighbors"
          type="word"
        />
      </v-card-text>
      <v-divider v-if="info" class="mx-4" />
      <v-card-text v-if="info" v-html="info" />
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
  },
  data: () => ({
    searchMode: null,
    searchModes: ["Space", "Label", "KO / Hypo", "Neighbors"],
    shouldShowMap: useShouldShowMap(),
  }),
  methods: {
    onSelect(type: string, e: string[]) {
      this.$emit("select", type, e);
    },
  },
};
</script>
