<template>
  <div>
    <simple-typeahead
      id="typeahead_id"
      placeholder="space"
      :items="items"
      :minInputLength="1"
      @onInput="onInputEventHandler"
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
  data() {
    return {
      items: [],
    };
  },
  methods: {
    onInputEventHandler(e) {
      console.log(e);
      const path = import.meta.env.VITE_SERVER_URL;
      axios
        .get(path + "/space/get/" + e.input)
        .then((res) => {
          this.items = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {},
};
</script>
