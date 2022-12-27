<template>
  <div>
    Word: {{ space.value.word }} <br />
    KO: {{ space.value.ko }} <br />
    Label: {{ space.value.label }} <br />
    Product: {{ space.value.product }} <br />
    Gene Name: {{ space.value.gene_name }} <br />
    Significant: {{ space.value.significant }} <br />
    Predicted Class: {{ space.value.predicted_class }} <br />
  </div>
</template>

<script lang="ts">
import { Space } from "../composables/spaces";

export default {
  name: "SpaceInfo",
  components: {},
  props: {
    space: {
      type: Object,
    },
  },
};
</script>
