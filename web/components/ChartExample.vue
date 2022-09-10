<template>
  <v-btn @click="a"></v-btn>
  <BarChart :chartData="testData" />
</template>

<script lang="ts">
import { BarChart } from "vue-chart-3";
export default {
  components: {
    BarChart,
  },
  data() {
    return {
      apiUrl: "http://127.0.0.1:5000/",
      testData: null,
    };
  },
  methods: {
    a() {
      console.log("ab");
      fetch(`${this.apiUrl}/plot/bar/K00053.1`)
        .then((res) => res.json())
        .then((res) => {
          this.testData = {
            labels: res.x,
            datasets: [
              {
                data: res.y,
              },
            ],
          };
        })
        .catch((err) => {
          console.error(err);
        });
    },
  },
};
</script>
