<template>
  <v-list lines="one">
    <v-list-item
      v-for="[k, v] in spaceToInfo(space)"
      :key="k"
      :subtitle="k"
      :title="v ? v : 'N/A'"
    ></v-list-item>
  </v-list>
</template>

<script lang="ts">
import { spaceToInfo } from "../composables/spaces";

export default {
  name: "SpaceInfo",
  components: {},
  props: {
    space: {
      type: Object,
    },
  },
  methods: {
    spaceToInfo(space: any) {
      return spaceToInfo(space);
    },
  },
};
</script>
