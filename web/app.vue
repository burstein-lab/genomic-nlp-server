<template>
  <div>
    <!-- <v-btn @click="getGifts">clickme</v-btn>
    <div>{{ a }}</div> -->
    <Search @select="(e: string) => onSelect('space', e)" type="space" />
    <Search @select="(e: string) => onSelect('label', e)" type="label" />
    <Map
      :zoom="zoom === '' ? 0 : +zoom"
      :latlng="latlng"
      :searchCollection="searchCollection"
    />
  </div>
</template>

<script setup lang="ts">
const latlng = ref({ lat: 0, lng: 0 });
const zoom = ref("0");
const searchCollection = ref([]);

const runtimeConfig = useRuntimeConfig();

function onSelect(type: string, e: string) {
  fetch(`${runtimeConfig.public.apiBase}/${type}/get/${e}`)
    .then((res) => res.json())
    .then((res) => {
      latlng.value = res.latlng;
      zoom.value = res.zoom;
      searchCollection.value = spacesToCollection(
        res.spaces,
        {
          z: res.zoom,
          x: res.latlng.lng,
          y: res.latlng.lat,
        },
        true
      );
    })
    .catch((error) => {
      // eslint-disable-next-line
      console.error(error);
    });
}
</script>
