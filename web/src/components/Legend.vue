<template>
  <v-btn color="info" size="small">
    Legend

    <v-tooltip activator="parent" location="top" id="legend-tooltip">
      <v-card style="opacity: 0.9">
        <v-list :lines="false" density="compact">
          <v-list-item
            v-for="item in items"
            :key="item"
            :style="
              clickedSpace?.value?.color === item.color
                ? theme.global.current.dark
                  ? 'background-color: #f9f9f9; color: #303030'
                  : 'background-color: #303030; color: #f9f9f9'
                : ''
            "
          >
            <template v-slot:prepend>
              <Circle :color="item.color" />
            </template>
            <v-list-item-title v-text="item.text"></v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>
    </v-tooltip>
  </v-btn>
</template>

<script lang="ts">
import { Space } from "@/composables/spaces";
import Circle from "./Circle.vue";
import { useTheme } from "vuetify";

export default {
  name: "Legend",
  components: {
    Circle,
  },
  props: {
    clickedSpace: {
      type: Object as () => Space | null,
    },
  },
  data: () => {
    return {
      theme: useTheme(),
      items: [],
    };
  },
  methods: {
    async getItems() {
      const rawRes = await fetch(
        `${import.meta.env.VITE_PUBLIC_URL}data/color_legend.tsv`
      );
      const tsv = await rawRes.text();
      tsv
        .split("\n")
        .slice(1)
        .forEach((line) => {
          if (!line) return;
          const [color, text] = line.split("\t");
          this.items.push({ text, color });
        });
    },
  },
  async beforeMount() {
    await this.getItems();
  },
};
</script>

<style>
#legend-tooltip .v-overlay__content {
  background: transparent !important;
}
</style>
