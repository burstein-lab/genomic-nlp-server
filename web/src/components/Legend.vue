<template>
  <v-card class="mx-auto" max-width="500">
    <v-list dense>
      <v-list-item-group v-model="selectedItem" color="primary">
        <v-list-item v-for="(item, i) in items" :key="i">
          <v-list-item-icon>
            <v-icon v-text="item.icon"></v-icon>
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
      selectedItem: 0,
      items: [
        { text: "Test 1", icon: "mdi-star" },
        { text: "Test 2", icon: "mdi-star" },
        { text: "Test 3", icon: "mdi-star" },
      ],
    };
  },
  methods: {},
};
</script>
