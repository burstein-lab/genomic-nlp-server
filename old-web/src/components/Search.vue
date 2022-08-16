<template>
  <simple-typeahead
    :placeholder="type"
    :items="items"
    :minInputLength="0"
    @onInput="onInputEventHandler"
    @selectItem="selectItemEventHandler"
  >
  </simple-typeahead>
</template>

<script>
import SimpleTypeahead from "vue3-simple-typeahead";
import "vue3-simple-typeahead/dist/vue3-simple-typeahead.css";
import axios from "axios";

export default {
  name: "Search",
  components: { SimpleTypeahead },
  emits: ["select"],
  props: {
    type: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      items: [],
      path: import.meta.env.VITE_SERVER_URL,
    };
  },
  methods: {
    onInputEventHandler(e) {
      axios
        .get(this.path + `/${this.type}/search?filter=` + e.input)
        .then((res) => {
          this.items = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    selectItemEventHandler(e) {
      axios
        .get(this.path + `/${this.type}/get/` + e)
        .then((res) => {
          console.log(res.data);
          this.$emit("select", res.data);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.onInputEventHandler({ input: "" });
  },
};
</script>
