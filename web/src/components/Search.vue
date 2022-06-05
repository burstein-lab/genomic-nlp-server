<template>
  <div>
    <simple-typeahead
      id="typeahead_id"
      placeholder="space"
      :items="items"
      :minInputLength="0"
      @onInput="onInputEventHandler"
      @selectItem="selectItemEventHandler"
    >
    </simple-typeahead>
  </div>
</template>

<script>
import SimpleTypeahead from "vue3-simple-typeahead";
import "vue3-simple-typeahead/dist/vue3-simple-typeahead.css";
import axios from "axios";

export default {
  name: "Search",
  components: { SimpleTypeahead },
  emits: ["select"],
  data() {
    return {
      items: [],
      path: import.meta.env.VITE_SERVER_URL,
    };
  },
  methods: {
    onInputEventHandler(e) {
      axios
        .get(this.path + "/space/search?filter=" + e.input)
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
        .get(this.path + "/space/get/" + e)
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
