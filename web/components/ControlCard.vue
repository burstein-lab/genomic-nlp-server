<template>
  <div>
    <v-card width="500" color="rgba(255, 255, 255, 0.8)">
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
    shouldShowMap: useShouldShowMap(),
  }),
  methods: {
    onSelect(type: string, e: string[]) {
      this.$emit("select", type, e);
    },
  },
};
</script>
