<template>
  <v-autocomplete
    color="primary"
    v-model="model"
    v-debounce:300ms="onInputChange"
    debounce-events="update:searchValue"
    @update:modelValue="$emit('search', model)"
    :items="items"
    :multiple="multiple"
    :chips="multiple"
    :closable-chips="multiple"
    :loading="isLoading"
    hide-no-data
    hide-selected
    hide-details
    :label="label"
    placeholder="Start typing to search"
  >
    <template v-slot:append-item>
      <div v-if="!done" v-intersect="onIntersect" class="ps-4 pt-4 pb-2">
        Loading more items...
      </div>
      <div v-else class="ps-4 pt-4 pb-2">No more results</div>
    </template>
  </v-autocomplete>
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
    page: 1,
    done: false,
    controller: new AbortController(),
  }),
  methods: {
    async onInputChange(value: string) {
      this.controller.abort();
      this.controller = new AbortController();
      this.isLoading = true;
      this.page = 1;
      this.done = false;
      this.search = value;
      const res = await this.fetchItems();
      this.done = res.length === 0;
      this.items = res;
      this.isLoading = false;
    },
    async onIntersect() {
      if (this.isLoading || this.done) return;

      this.isLoading = true;
      this.page += 1;
      const res = await this.fetchItems();
      this.done = res.length === 0;
      this.items = [...this.items, ...res];
      this.isLoading = false;
    },
    async fetchItems() {
      const rawRes = await fetch(
        `${
          import.meta.env.VITE_SERVER_URL
        }/${this.type.toLowerCase()}/search?filter=${this.search.toLowerCase()}&page=${
          this.page
        }`,
        { signal: this.controller.signal }
      );
      return await rawRes.json();
    },
  },
  created() {
    this.onInputChange("");
  },
};
</script>
