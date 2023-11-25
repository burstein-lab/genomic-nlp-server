<template>
  <v-btn color="info" size="small">
    Legend

    <v-tooltip activator="parent" location="top">
      <v-card class="custom-card">
        <v-list :lines="false" density="compact">
          <v-list-item
            v-for="item in items"
            :key="item.color"
            :color="selectedItem === item.color ? 'info' : undefined"
            size="small"
            active-color="info"
            v-model="selectedItem"
            style="font-size: 0.75rem"
          >
            <template v-slot:prepend>
              <v-icon :color="item.color" class="me-2">mdi-circle</v-icon>
            </template>
            <v-list-item-title v-text="item.text"></v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>
    </v-tooltip>
  </v-btn>
</template>

<script lang="ts">
export default {
  name: "Legend",
  data: () => {
    return {
      isActive: false,
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

<style scoped>
.custom-card {
  background-color: transparent; /* Set background color to transparent */
  box-shadow: none; /* Remove box shadow */
  opacity: 0.9;
}
</style>
