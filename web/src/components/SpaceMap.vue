<template>
  <div>
    <div style="height: 98vh; width: 98vw">
      <l-map
        id="mapRef"
        ref="mapRef"
        v-model="zoom"
        v-model:zoom="zoom"
        crs="Simple"
        :center="[-512, 512]"
        :maxBounds="[
          [tileSize * 0.5, -tileSize * 0.5],
          [-tileSize * 1.5, tileSize * 1.5],
        ]"
        :boundsViscosity="0.5"
        :options="{ zoomControl: false }"
        @ready="onMapReady(this)"
      >
        <l-control-zoom position="bottomright"></l-control-zoom>
        <l-tile-layer
          v-if="isMapVisible"
          ref="tileLayerRef"
          :url="publicAssetsUrl + 'map/{z}/space_by_label_{x}_{y}.png'"
          layer-type="base"
          name="OpenStreetMap"
          :max-zoom="5"
          :min-zoom="0"
          :tileSize="tileSize"
          @ready="onTileLayerReady(this)"
        />

        <l-geo-json
          :geojson="searchCollection"
          :ref="'geoJsonSearchRef'"
          :options="getJsonOptions"
        />
        <l-geo-json
          v-for="[k, v] in collections"
          :ref="'geoJson' + k + 'Ref'"
          :geojson="v"
          :options="getJsonOptions"
        />
        <l-control ref="controlRef" position="topleft">
          <ControlCard :loading="loading" @search="onSearch" />
        </l-control>
      </l-map>
    </div>
  </div>
</template>

<script lang="ts">
import {
  LMap,
  LIcon,
  LTileLayer,
  LMarker,
  LControlZoom,
  LTooltip,
  LPopup,
  LImageOverlay,
  LGeoJson,
  LPolyline,
  LPolygon,
  LControl,
  LRectangle,
} from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import {
  useZoom,
  useLatLng,
  useHoverPoint,
  useClickPoint,
  useShouldShowMap,
} from "../composables/states";
import ControlCard from "./ControlCard.vue";
import { spacesToCollection } from "../composables/spaces";

export default {
  components: {
    LMap,
    LIcon,
    LTileLayer,
    LControlZoom,
    LMarker,
    LImageOverlay,
    LTooltip,
    LPopup,
    LControl,
    LPolyline,
    LGeoJson,
    LPolygon,
    LRectangle,
    ControlCard,
  },
  data() {
    return {
      latlng: useLatLng(),
      zoom: useZoom(),
      publicAssetsUrl: import.meta.env.VITE_PUBLIC_URL,
      apiUrl: import.meta.env.VITE_SERVER_URL,
      getJsonOptions: {
        onEachFeature: this.onEachFeature,
      },
      hoverPoint: useHoverPoint(),
      clickPoint: useClickPoint(),
      isMapVisible: useShouldShowMap(),
      collections: new Map(),
      tileSize: 1024,
      searchCollection: null,
      loading: false,
    };
  },
  async beforeMount() {
    const { circleMarker } = await import("leaflet/dist/leaflet-src.esm");
    // And now the Leaflet circleMarker function can be used by the options:
    this.getJsonOptions.pointToLayer = (feature, latlng) =>
      circleMarker(latlng, {
        radius: 10,
        fillColor: feature.properties.isSearch ? "#007800" : "#ff7800",
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8,
      });
  },
  methods: {
    onTileLayerReady(self) {
      // this != component instance on ready event from some reason...
      self.tileLayer = this.$refs.tileLayerRef.leafletObject;
      // https://leafletjs.com/reference.html#tilelayer
      self.tileLayer.on("tileunload", function (event) {
        self.collections.delete(
          self.coordsToString(event.coords.z, event.coords.x, event.coords.y)
        );
      });
      self.tileLayer.on("tileloadstart", function (event) {
        self.getFeatures(event.coords);
      });
    },
    geoJsonObj(k) {
      // When using v-for, ref is a list.
      return this.$refs[`geoJson${k}Ref`][0].leafletObject;
    },
    onMapReady(self) {
      self.map = this.$refs.mapRef.leafletObject;
    },
    getFeatures(coords) {
      fetch(`${this.apiUrl}/points?z=${coords.z}&x=${coords.x}&y=${coords.y}`)
        .then((res) => res.json())
        .then((res) => {
          this.collections.set(
            this.coordsToString(coords.z, coords.x, coords.y),
            spacesToCollection(res["features"], coords, false)
          );
        })
        .catch((err) => {
          console.error(err);
        });
    },
    changeIcon() {
      this.iconWidth += 2;
      if (this.iconWidth > this.iconHeight) {
        this.iconWidth = Math.floor(this.iconHeight / 2);
      }
    },
    onEachFeature(feature, layer) {
      layer.on({
        mouseover: this.highlightFeature,
        mouseout: this.resetHighlight,
        click: (e) => {
          this.clickPoint = e.target.feature.properties;
          this.zoomToFeature(e.latlng, this.zoom);
        },
      });
    },
    highlightFeature(e) {
      if (
        this.clickPoint &&
        this.clickPoint.id === e.target.feature.properties.id
      ) {
        return;
      }
      const layer = e.target;
      layer.setStyle({
        weight: 5,
        color: "#666",
        dashArray: "",
        fillOpacity: 0.7,
      });
      layer.bringToFront();
      this.hoverPoint = e.target.feature.properties;
    },
    resetHighlight(e) {
      let obj;
      if (e.target.feature.properties.isSearch) {
        obj = this.$refs[`geoJsonSearchRef`].leafletObject;
      } else {
        obj = this.geoJsonObj(
          this.coordsToString(
            e.target.feature.properties.zoom,
            e.target.feature.properties.tileX,
            e.target.feature.properties.tileY
          )
        );
      }
      obj.resetStyle(e.target);
      this.hoverPoint = null;
    },
    zoomToFeature(latlng, zoom: number) {
      this.map.setView(latlng, zoom);
    },
    coordsToString(z: number, x: number, y: number) {
      return `${z}-${x}-${y}`;
    },
    onSearch(type: string, e: string[], k: number) {
      console.log(type);
      this.loading = true;
      const url = new URL(`${this.apiUrl}/${type}/get/${e.toString()}`);
      if (type === "neighbors") {
        url.searchParams.append("k", k.toString());
      }
      fetch(url.href)
        .then((res) => res.json())
        .then((res) => {
          this.latlng = res.latlng;
          this.zoom = res.zoom;
          this.searchCollection = spacesToCollection(
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
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
  watch: {
    zoom(value: number) {
      console.log(value);
    },
    searchCollection(value) {
      this.zoomToFeature(this.latlng, this.zoom);
    },
  },
};
</script>

<style>
.leaflet-pane {
  z-index: 1;
}

#mapRef {
  background: rgb(var(--v-theme-background));
}
</style>
