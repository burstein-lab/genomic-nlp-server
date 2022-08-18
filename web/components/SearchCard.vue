<template>
  <div>
    <v-card width="500">
      <v-card-title> Search Spaces </v-card-title>
      <v-card-text>
        <v-switch
          v-model="shouldShowMap"
          color="primary"
          label="Show Map"
          hide-details
        ></v-switch>
        <search @select="(e: string[]) => onSelect('space', e)" type="Space" />
        <search @select="(e: string[]) => onSelect('label', e)" type="Label" />
        <search
          @select="(e: string[]) => onSelect('ko', e)"
          type="KO"
          multiple
        />
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
export default {
  data: () => ({
    shouldShowMap: useShouldShowMap(),
  }),
  methods: {
    onSelect(type: string, e: string[]) {
      this.$emit("select", type, e);
    },
  },
};
</script>
