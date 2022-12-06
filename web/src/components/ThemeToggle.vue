<template>
  <v-btn icon color="primary" @click="toggleTheme">
    <v-icon>mdi-theme-light-dark</v-icon>
  </v-btn>
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
