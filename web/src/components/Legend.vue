<template>
  <v-card width="300">
    <v-list nav dense>
      <v-list-item
        v-for="item in items"
        :key="item.color"
        :color="selectedItem === item.color ? 'info' : undefined"
        dense
      >
        <v-list-item-icon>
          <v-icon :color="item.color">mdi-sqaure</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title v-text="item.text"></v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script lang="ts">
export default {
  name: "Legend",
  data: () => {
    return {
      serverUrl: new URL(import.meta.env.VITE_SERVER_URL),
      selectedItem: "#808080",
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
