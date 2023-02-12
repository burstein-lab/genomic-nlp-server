<template>
  <v-autocomplete
    color="primary"
    v-model="model"
    v-debounce:500ms="onInputChange"
    :debounce-events="'update:searchValue'"
    @update:modelValue="$emit('search', model)"
    :items="items"
    :multiple="multiple"
    :loading="isLoading"
    hide-no-data
    hide-selected
    hide-details
    :label="label"
    placeholder="Start typing to search"
  />
</template>

<script lang="ts">
import { vue3Debounce } from "vue-debounce";

export default {
  name: "Search",
  emits: ["search"],
  directives: {
    debounce: vue3Debounce({ lock: true }),
  },
  props: {
    multiple: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: true,
    },
  },
  data: () => ({
    items: [],
    isLoading: false,
    model: null,
    search: null as string | null,
    apiUrl: import.meta.env.VITE_SERVER_URL,
  }),
  methods: {
    async onInputChange(value: string) {
      // Items have already been requested
      if (this.isLoading) return;

      this.isLoading = true;

      // Lazily load input items
      const rawRes = await fetch(
        `${
          this.apiUrl
        }/${this.type.toLowerCase()}/search?filter=${value.toLowerCase()}`
      );
      const res = await rawRes.json();
      this.items = res;
      this.isLoading = false;
    },
  },
  created() {
    this.onInputChange("");
  },
};
</script>
