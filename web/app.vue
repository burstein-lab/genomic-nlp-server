<template>
  <div>
    <!-- <v-btn @click="getGifts">clickme</v-btn>
    <div>{{ a }}</div> -->
    <Map />
  </div>
</template>

<script setup lang="ts">
async function getGifts() {
  const result = await useFetch("http://127.0.0.1:5000/hello");
  a.value = result.data;
}

const a = ref();
</script>
