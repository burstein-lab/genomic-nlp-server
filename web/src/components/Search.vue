<template>
  <v-autocomplete
    color="info"
    :key="searchMode"
    v-debounce:300ms="onInputChange"
    @update:modelValue="onChoose"
    v-model="searchValue"
    :items="items"
    :multiple="searchType?.multiple"
    :chips="searchType?.multiple"
    :closable-chips="searchType?.multiple"
    :loading="isLoading"
    hide-no-data
    hide-details
    :label="searchType.label"
    auto-select-first
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
import { searchModeToType, SearchMode } from "@/composables/spaces";

export default {
  name: "Search",
  emits: ["search"],
  directives: {
    debounce: vue3Debounce({ lock: true }),
  },
  props: {
    searchMode: {
      type: String,
      required: true,
    },
  },
  data: () => {
    return {
      searchModeToType,
      items: [] as string[],
      isLoading: false,
      searchValue: null as null | string | string[],
      searchTerm: "",
      page: 1,
      done: false,
      controller: new AbortController(),
    };
  },
  beforeMount() {
    if (!this.searchType) return;

    if (this.searchType?.multiple) {
      this.searchValue = this.$route.query.searchValue
        ? this.$route.query.searchValue.split(",")
        : null;
    } else {
      this.searchValue = this.$route.query.searchValue
        ? this.$route.query.searchValue
        : null;
      this.searchTerm = this.searchValue ? (this.searchValue as string) : "";
    }
    this.onInputChange(this.searchTerm);
  },
  computed: {
    searchType(): SearchMode {
      return searchModeToType[this.searchMode];
    },
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
      this.done = res.done;
      this.items = res.items;
      this.isLoading = false;
    },
    async onIntersect(val: string) {
      if (this.isLoading || this.done) return;

      this.isLoading = true;
      this.page += 1;
      const res = await this.fetchItems();
      this.done = res.done;
      this.items = [...this.items, ...res.items];
      this.isLoading = false;
    },
    async onChoose(val: string | string[]) {
      this.isLoading = false;
      this.controller.abort();
      this.controller = new AbortController();
      this.$emit("search", this.searchType.emit, val);
    },
    async fetchItems(): Promise<{ done: boolean; items: string[] }> {
      const rawRes = await fetch(
        `${
          import.meta.env.VITE_SERVER_URL
        }/${this.searchType.type.toLowerCase()}/search?filter=${this.searchTerm.toLowerCase()}&page=${
          this.page
        }`,
        { signal: this.controller.signal }
      );
      return await rawRes.json();
    },
  },
};
</script>
