<template>
  <v-card width="300">
    <v-list dense>
      <v-list-item-group v-model="selectedItem" color="primary">
        <v-list-item v-for="(item, i) in items" :key="i">
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title v-text="item.text"></v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-card>
</template>

<script lang="ts">
export default {
  name: "Legend",
  data: () => {
    return {
      serverUrl: new URL(import.meta.env.VITE_SERVER_URL),
      selectedItem: 0,
      items: [
        { text: "Test 1", icon: "mdi-star" },
        { text: "Test 2", icon: "mdi-star" },
        { text: "Test 3", icon: "mdi-star" },
      ],
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
          const [color, text] = line.split("\t");
          this.items.push({ text, icon: "mdi-star" });
        });
    },
  },
  async beforeMount() {
    await this.getItems();
  },
};
</script>
