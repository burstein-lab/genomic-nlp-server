<template>
  <div>
    <div>{{ counter }}</div>
    <test></test>
    <v-container fluid>
      <v-row>
        <v-col>
          <search-card @select="onSelect" />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <space-map
            :shouldShowMap="shouldShowMap"
            :searchCollection="searchCollection"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
const latlng = useLatLng();
const zoom = useZoom();
const shouldShowMap = useShouldShowMap();
const searchCollection = ref(null);

const counter = useState("counter", () => Math.round(Math.random() * 1000));

const runtimeConfig = useRuntimeConfig();

function onSelect(type: string, e: string[]) {
  fetch(`${runtimeConfig.public.apiBase}/${type}/get/${e.toString()}`)
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
      console.error(error);
    });
}

function onShowMap(value: boolean) {
  shouldShowMap.value = value;
}
</script>
