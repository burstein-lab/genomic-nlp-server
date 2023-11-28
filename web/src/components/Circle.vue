<template>
  <div
    class="circle"
    :style="`
        border: 2px solid ${theme.global.current.dark ? '#303030' : '#f9f9f9'};
        background-color: ${color};
        height: 20px;
        width: 20px;
        border-radius: 50%;
        margin-right: 8px;
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
