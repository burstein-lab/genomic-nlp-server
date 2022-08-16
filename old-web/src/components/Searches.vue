<template>
  <div>
    <search id="search_id_space" type="space" />
    <search id="search_id_label" type="label" />
  </div>
</template>

<script>
import SimpleTypeahead from "vue3-simple-typeahead";
import "vue3-simple-typeahead/dist/vue3-simple-typeahead.css";

import Search from "../components/Search.vue";

export default {
  name: "Searches",
  components: { SimpleTypeahead, Search },
  emits: ["select"],
  data() {
    return {};
  },
  methods: {},
  created() {},
};
</script>
