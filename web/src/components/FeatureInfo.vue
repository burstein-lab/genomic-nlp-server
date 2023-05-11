<template>
  <v-list lines="one">
    <v-list-item
      v-for="[k, v] in spaceToInfo(feature.properties.value)"
      :key="k"
      :subtitle="k"
      :title="v === undefined || v === null ? 'N/A' : v.toString()"
    ></v-list-item>
  </v-list>
</template>

<script lang="ts">
import { spaceToInfo, Feature } from "@/composables/spaces";

export default {
  name: "FeatureInfo",
  components: {},
  props: {
    feature: {
      type: Object as () => Feature | null,
    },
  },
  methods: {
    spaceToInfo(space: any) {
      return spaceToInfo(space);
    },
  },
};
</script>
