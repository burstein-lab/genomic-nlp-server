<template>
  <h1>abc</h1>
  <h1>{{ msg }}</h1>
</template>

<script>
import axios from "axios";

export default {
  name: "Ping",
  data() {
    return {
      msg: "abc",
    };
  },
  methods: {
    getMessage() {
      const path = import.meta.env.VITE_SERVER_URL;
      axios.get(path)
        .then((res) => {
          this.msg = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>
