<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col>
          <v-card width="500">
            <v-card-title> Search Spaces </v-card-title>
            <v-card-text>
              <Search
                @select="(e: string[]) => onSelect('space', e)"
                type="Space"
              />
              <Search
                @select="(e: string[]) => onSelect('label', e)"
                type="Label"
              />
              <v-divider />
              <Search
                @select="(e: string[]) => onSelect('ko', e)"
                type="KO"
                multiple
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <Map
            :zoom="zoom === '' ? 0 : +zoom"
            :latlng="latlng"
            :searchCollection="searchCollection"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
const latlng = ref({ lat: 0, lng: 0 });
const zoom = ref("0");
const searchCollection = ref(null);

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
</script>
