<template>
  <div
    class="circle"
    :style="`
        border: 2px solid ${theme.global.current.dark ? '#303030' : '#f9f9f9'};
        background-color: ${color};
        height: 24px;
        width: 24px;
        border-radius: 50%;
    `"
  ></div>
</template>

<script lang="ts">
import { useTheme } from "vuetify";

export default {
  name: "Circle",
  props: {
    color: {
      type: String,
    },
  },
  data: () => {
    return {
      theme: useTheme(),
    };
  },
};
</script>
