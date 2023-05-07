<template>
  <v-switch
    @update:modelValue="toggleTheme"
    color="primary"
    inset
    label="Light Theme"
    hide-details
  />
</template>

<script lang="ts">
import { useTheme } from "vuetify";

export default {
  name: "ThemeToggle",
  setup() {
    const theme = useTheme();
    return {
      theme,
      toggleTheme: () =>
        (theme.global.name.value = theme.global.current.value.dark
          ? "light"
          : "dark"),
    };
  },
};
</script>
