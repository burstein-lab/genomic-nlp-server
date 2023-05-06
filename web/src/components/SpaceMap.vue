<template>
  <div style="height: 100vh; width: 100vw">
    <l-map
      id="mapRef"
      ref="mapRef"
      v-model:zoom="zoom"
      crs="Simple"
      :bounds="[-(tileSize / 2), tileSize / 2]"
      :maxBounds="[
        [tileSize * 0.5, -tileSize * 0.5],
        [-tileSize * 1.5, tileSize * 1.5],
      ]"
      :boundsViscosity="0.5"
      :options="{
        zoomControl: false,
        wheelPxPerZoomLevel: 120,
      }"
      @ready="onMapReady(this)"
    >
      <l-control-zoom position="bottomright" />
      <l-tile-layer
        v-if="isMapVisible"
        ref="tileLayerRef"
        url="map/{z}/space_by_label_{x}_{y}.png"
        layer-type="base"
        name="OpenStreetMap"
        :max-zoom="maxZoom"
        :min-zoom="0"
        :tileSize="tileSize"
        @ready="onTileLayerReady(this)"
      />
      <l-geo-json
        :geojson="searchCollection"
        :key="zoom"
        :ref="'geoJsonSearchRef'"
        :options="getJsonOptions"
      />
      <l-geo-json
        v-for="[k, v] in collections"
        :key="k"
        :ref="'geoJson' + k + 'Ref'"
        :geojson="v"
        :options="getJsonOptions"
      />
      <l-control ref="controlRef" position="topleft">
        <ControlCard
          @cancelClickPoint="onCancelClickPoint"
          @resetClickPoint="onResetClickPoint"
          @centerPoint="onCenterPoint"
          @setMap="onSetMap"
          @setMapVisibility="(shouldShowMap) => (isMapVisible = shouldShowMap)"
        />
      </l-control>
    </l-map>
  </div>
</template>

<script lang="ts">
import {
  LMap,
  LIcon,
  LTileLayer,
  LMarker,
  LControl,
  LControlZoom,
  LTooltip,
  LPopup,
  LImageOverlay,
  LGeoJson,
  LPolyline,
  LCircleMarker,
  LPolygon,
  LFeatureGroup,
  LRectangle,
} from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import { useHoverPoint, useClickedCircle } from "@/composables/states";
import ControlCard from "./ControlCard.vue";
import {
  SpacesResponse,
  spacesToCollection,
  Coords,
  LatLng,
  unselectedPointStyle,
  selectedPointStyle,
  Feature,
  highlightedPointStyle,
} from "@/composables/spaces";

export default {
  name: "SpaceMap",
  components: {
    LMap,
    LIcon,
    LCircleMarker,
    LTileLayer,
    LControlZoom,
    LFeatureGroup,
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
    const maxZoom = Number(import.meta.env.VITE_MAX_ZOOM);
    const collections = new Map();
    return {
      maxZoom: maxZoom,
      zoom: 0,
      getJsonOptions: {
        onEachFeature: this.onEachFeature,
      },
      hoverPoint: useHoverPoint(),
      clickedCircle: useClickedCircle(),
      isMapVisible: true,
      collections: collections,
      tileSize: 1024,
      searchCollection: { type: "FeatureCollection", features: [] },
      map: null,
    };
  },
  async beforeMount() {
    const { circleMarker } = await import("leaflet/dist/leaflet-src.esm");
    this.getJsonOptions.pointToLayer = (feature, latlng: LatLng) => {
      if (
        this.clickedCircle &&
        this.clickedCircle.feature.properties.id === feature.properties.id
      ) {
        const result = circleMarker(latlng, selectedPointStyle(feature));
        this.clickedCircle = result;
        return result;
      }

      return circleMarker(latlng, unselectedPointStyle(feature));
    };
  },
  methods: {
    onSetMap(res: SpacesResponse) {
      if (!res) {
        this.searchCollection = { type: "FeatureCollection", features: [] };
        return;
      }

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
      this.zoomToFeature(res.latlng, res.zoom);
    },
    onTileLayerReady(self) {
      // this != component instance on ready event from some reason...
      self.tileLayer = this.$refs.tileLayerRef.leafletObject;
      // https://leafletjs.com/reference.html#tilelayer
      self.tileLayer.on("tileunload", async (event) => {
        const unload = () => {
          const existed = self.collections.delete(
            self.coordsToString(event.coords.z, event.coords.x, event.coords.y)
          );

          if (!existed) {
            setTimeout(unload, 300);
          }
        };

        unload();
      });
      self.tileLayer.on("tileload", async (event) => {
        await self.getFeatures(event.coords);
      });
    },
    geoJsonObj(k: string) {
      // When using v-for, ref is a list.
      return this.$refs[`geoJson${k}Ref`][0].leafletObject;
    },
    onResetClickPoint() {
      if (!this.clickedCircle) return;
      this.clickedCircle.setStyle(
        unselectedPointStyle(this.clickedCircle.feature)
      );
    },
    onMapReady(self) {
      self.map = this.$refs.mapRef.leafletObject;
      self.map.setView(
        {
          lat: -self.tileSize / 2,
          lng: self.tileSize / 2,
        },
        0
      );
    },
    async getFeatures(coords: Coords) {
      const rawRes = await fetch(
        `map/${coords.z}/space_by_label_${coords.x}_${coords.y}.json`
      );

      let features = [];
      if (rawRes.status !== 404) {
        const res = await rawRes.json();
        features = res["features"];
      }

      this.collections.set(
        this.coordsToString(coords.z, coords.x, coords.y),
        spacesToCollection(features, coords, false)
      );
    },
    onEachFeature(feature, layer) {
      layer.on({
        mouseover: () => {
          this.highlightFeature(layer, feature);
        },
        mouseout: () => {
          this.resetHighlight(layer, feature);
        },
        click: () => {
          this.onClickPoint(layer, feature);
        },
      });
    },
    highlightFeature(layer, feature) {
      if (
        this.clickedCircle &&
        this.clickedCircle.feature.properties.id === feature.properties.id
      ) {
        return;
      }
      layer.setStyle(highlightedPointStyle);
      // TODO: layer.bringToFront();
      this.hoverPoint = feature.properties;
    },
    resetHighlight(layer, feature) {
      if (
        this.clickedCircle &&
        this.clickedCircle.feature.properties.id === feature.properties.id
      ) {
        return;
      }
      layer.setStyle(unselectedPointStyle(feature));
      this.hoverPoint = null;
    },
    onClickPoint(layer, feature: Feature) {
      if (this.clickedCircle) {
        this.clickedCircle.setStyle(
          unselectedPointStyle(this.clickedCircle.feature)
        );
      }

      this.clickedCircle = layer;
      this.hoverPoint = null;
      this.zoomToFeature(
        {
          lat: feature.geometry.coordinates[1],
          lng: feature.geometry.coordinates[0],
        },
        this.zoom
      );
      this.clickedCircle.setStyle(
        selectedPointStyle(this.clickedCircle.feature)
      );
    },
    zoomToFeature(latlng: LatLng, zoom: number) {
      this.map.setView(latlng, zoom);
    },
    coordsToString(z: number, x: number, y: number) {
      return `${z}-${x}-${y}`;
    },
    onCancelClickPoint() {
      this.clickedCircle.setStyle(
        unselectedPointStyle(this.clickedCircle.feature)
      );
    },
    onCenterPoint() {
      this.zoomToFeature(
        {
          lat: this.clickedCircle.feature.geometry.coordinates[1],
          lng: this.clickedCircle.feature.geometry.coordinates[0],
        },
        this.zoom
      );
    },
  },
  watch: {
    zoom(value: number) {
      console.log(value);
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
