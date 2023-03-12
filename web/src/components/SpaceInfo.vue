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
      return spaceToInfo(space);
    },
  },
};
</script>
