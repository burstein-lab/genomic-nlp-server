<template>
  <v-autocomplete
    color="info"
    v-debounce:300ms="(v: string) => onInputChange(searchMode, v)"
    debounce-events="update:searchValue"
    v-model="searchValue"
    @update:modelValue="onChoose"
    :items="items"
    :multiple="multiple"
    :chips="multiple"
    :closable-chips="multiple"
    :loading="isLoading"
    hide-no-data
    hide-details
    :label="searchModeToType[searchMode].label"
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
import { searchModeToType } from "@/composables/spaces";

export default {
  name: "Search",
  emits: ["search"],
  directives: {
    debounce: vue3Debounce({ lock: true }),
  },
  data: () => ({
    searchModeToType,
    items: [],
    isLoading: false,
    searchValue: null as string | string[],
    searchTerm: "",
    page: 1,
    done: false,
    controller: new AbortController(),
  }),
  async beforeMount() {
    console.log("Component is about to be mounted");
  },
  mounted() {
    console.log("Component is mounted");
  },
  created() {
    console.log("Component is created");
  },
  beforeUpdate() {
    console.log("Component is about to be updated");
  },
  computed: {
    searchMode(): string {
      const val = this.$route.query.searchMode
        ? this.$route.query.searchMode
        : "KEGG ortholog";

      if (searchModeToType[val].multiple) {
        this.searchValue = this.$route.query.searchValue
          ? this.$route.query.searchValue.split(",")
          : null;
      } else {
        this.searchValue = this.$route.query.searchValue
          ? this.$route.query.searchValue
          : null;
        this.searchTerm = this.searchValue ? (this.searchValue as string) : "";
      }
      this.onInputChange(this.searchTerm, val);
      return val;
    },
    multiple(): boolean {
      return searchModeToType[this.searchMode].multiple;
    },
  },
  methods: {
    async onInputChange(searchMode: string, value: string) {
      this.controller.abort();
      this.controller = new AbortController();
      this.isLoading = true;
      this.page = 1;
      this.done = false;
      this.searchTerm = value;
      const res = await this.fetchItems(searchMode);
      this.done = res.done;
      this.items = res.items;
      this.isLoading = false;
    },
    async onIntersect(val: string) {
      if (this.isLoading || this.done) return;

      this.isLoading = true;
      this.page += 1;
      const res = await this.fetchItems(this.searchMode);
      this.done = res.done;
      this.items = [...this.items, ...res.items];
      this.isLoading = false;
    },
    async onChoose(val: string | string[]) {
      this.isLoading = false;
      this.controller.abort();
      this.controller = new AbortController();
      this.$emit("search", searchModeToType[this.searchMode].emit, val);
    },
    async fetchItems(searchMode: string) {
      const rawRes = await fetch(
        `${import.meta.env.VITE_SERVER_URL}/${searchModeToType[
          searchMode
        ].type.toLowerCase()}/search?filter=${this.searchTerm.toLowerCase()}&page=${
          this.page
        }`,
        { signal: this.controller.signal }
      );
      return await rawRes.json();
    },
  },
};
</script>
