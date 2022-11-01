<template>
  <v-autocomplete
    v-model="model"
    v-model:search="search"
    @update:modelValue="select"
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
export default {
  name: "Search",
  emits: ["select"],
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
    select() {
      this.$emit("select", this.model);
    },
  },
  created() {
    this.search = "";
  },
  watch: {
    search(val: string) {
      // Items have already been requested
      if (this.isLoading) return;

      this.isLoading = true;

      // Lazily load input items
      fetch(
        `${
          this.apiUrl
        }/${this.type.toLowerCase()}/search?filter=${val.toLowerCase()}`
      )
        .then((res) => res.json())
        .then((res) => {
          this.items = res;
        })
        .catch((err) => {
          console.log(err);
        })
        .finally(() => (this.isLoading = false));
    },
  },
};
</script>
