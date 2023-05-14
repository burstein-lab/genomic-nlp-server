<template>
  <v-autocomplete
    color="info"
    v-debounce:300ms="onInputChange"
    debounce-events="update:searchValue"
    v-model="searchValue"
    @update:modelValue="onChoose"
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
    density="comfortable"
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
    searchValue: "" as string | string[],
    searchTerm: "",
    page: 1,
    done: false,
    controller: new AbortController(),
  }),
  async beforeMount() {
    if (this.multiple) {
      this.searchValue = this.$route.query.searchValue?.split(",");
    } else {
      this.searchValue = this.$route.query.searchValue;
      this.searchTerm = this.searchValue ? (this.searchValue as string) : "";
    }
    await this.onInputChange(this.searchTerm);
  },
  methods: {
    async onInputChange(value: string) {
      this.controller.abort();
      this.controller = new AbortController();
      this.isLoading = true;
      this.page = 1;
      this.done = false;
      this.searchTerm = value;
      const res = await this.fetchItems();
      this.done = res.length === 0;
      this.items = res;
      this.isLoading = false;
    },
    async onIntersect(val: string) {
      if (this.isLoading || this.done) return;

      this.isLoading = true;
      this.page += 1;
      const res = await this.fetchItems();
      this.done = res.length === 0;
      this.items = [...this.items, ...res];
      this.isLoading = false;
    },
    async onChoose(val: string | string[]) {
      this.isLoading = false;
      this.controller.abort();
      this.controller = new AbortController();
      this.$emit("search", val);
    },
    async fetchItems() {
      const rawRes = await fetch(
        `${
          import.meta.env.VITE_SERVER_URL
        }/${this.type.toLowerCase()}/search?filter=${this.searchTerm.toLowerCase()}&page=${
          this.page
        }`,
        { signal: this.controller.signal }
      );
      return await rawRes.json();
    },
  },
};
</script>
