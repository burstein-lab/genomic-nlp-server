<template>
  <div v-html="spaceToInfo(space)" />
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
      const infoMap = spaceToInfo(space);
      return Array.from(infoMap, ([key, value]) => `${key}: ${value}`).join(
        "<br />"
      );
    },
  },
};
</script>
