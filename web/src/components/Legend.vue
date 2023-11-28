<template>
  <v-btn color="info" size="small">
    Legend

    <v-tooltip activator="parent" location="top" id="legend-tooltip">
      <v-card style="opacity: 0.9">
        <v-list :lines="false" density="compact">
          <v-list-item
            v-for="item in items"
            :key="item.color"
            color="success"
            :input-value="true"
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

<style>
#legend-tooltip .v-overlay__content {
  background: transparent !important;
}
</style>
