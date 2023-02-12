<template>
  <div style="height: 100vh; width: 100vw">
    <l-map
      id="mapRef"
      ref="mapRef"
      v-model="zoom"
      v-model:zoom="zoom"
      crs="Simple"
      :center="[-(tileSize / 2), tileSize / 2]"
      :maxBounds="[
        [tileSize * 0.5, -tileSize * 0.5],
        [-tileSize * 1.5, tileSize * 1.5],
      ]"
      :boundsViscosity="0.5"
      :options="{ zoomControl: false }"
      @ready="onMapReady(this)"
    >
      <l-control-zoom position="bottomright" />
      <l-tile-layer
        v-if="isMapVisible"
        ref="tileLayerRef"
        :url="publicAssetsUrl + 'map/{z}/space_by_label_{x}_{y}.png'"
        layer-type="base"
        name="OpenStreetMap"
        :max-zoom="maxZoom"
        :min-zoom="0"
        :tileSize="tileSize"
        @ready="onTileLayerReady(this)"
      />
      <l-geo-json
        :geojson="searchCollection"
        :ref="'geoJsonSearchRef'"
        :options="getJsonOptions"
      />
      <div v-for="[k, v] in collections" :key="k">
        <l-geo-json
          v-for="[k2, v2] in v"
          v-if="k == zoom"
          :key="k2"
          :ref="'geoJson' + k2 + 'Ref'"
          :geojson="v2"
          :options="getJsonOptions"
        />
      </div>
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
import { useZoom, useHoverPoint, useClickPoint } from "@/composables/states";
import ControlCard from "./ControlCard.vue";
import { spacesToCollection, Coords, LatLng } from "@/composables/spaces";

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
    for (let i = 0; i <= maxZoom; i++) {
      collections.set(i, new Map());
    }

    return {
      maxZoom: maxZoom,
      zoom: useZoom(),
      publicAssetsUrl: import.meta.env.VITE_PUBLIC_URL,
      getJsonOptions: {
        onEachFeature: this.onEachFeature,
      },
      hoverPoint: useHoverPoint(),
      clickPoint: useClickPoint(),
      clickPointTarget: null,
      isMapVisible: true,
      collections: collections,
      tileSize: 1024,
      searchCollection: null,
      map: null,
    };
  },
  async beforeMount() {
    const { circleMarker } = await import("leaflet/dist/leaflet-src.esm");
    // And now the Leaflet circleMarker function can be used by the options:
    this.getJsonOptions.pointToLayer = (feature, latlng: LatLng) =>
      circleMarker(latlng, {
        radius: this.zoom + 2,
        fillColor: feature.properties.value.color, // TODO: border color by feature.properties.isSearch ? "#007800" : "#ff7800",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8,
      });
  },
  methods: {
    onSetMap(latlng: LatLng, zoom: number, searchCollection) {
      this.zoom = zoom;
      this.searchCollection = searchCollection;
      this.zoomToFeature(latlng, zoom);
    },
    onTileLayerReady(self) {
      // this != component instance on ready event from some reason...
      self.tileLayer = this.$refs.tileLayerRef.leafletObject;
      // https://leafletjs.com/reference.html#tilelayer
      self.tileLayer.on("tileunload", function (event) {
        self.collections
          .get(event.coords.z)
          .delete(
            self.coordsToString(event.coords.z, event.coords.x, event.coords.y)
          );
      });
      self.tileLayer.on("tileloadstart", function (event) {
        self.getFeatures(event.coords);
      });
    },
    geoJsonObj(k: string) {
      // When using v-for, ref is a list.
      return this.$refs[`geoJson${k}Ref`][0].leafletObject;
    },
    onResetClickPoint() {
      const e = this.clickPointTarget;
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
    },
    onMapReady(self) {
      self.map = this.$refs.mapRef.leafletObject;
    },
    getFeatures(coords: Coords) {
      fetch(
        `${this.publicAssetsUrl}map/${coords.z}/space_by_label_${coords.x}_${coords.y}.json`
      )
        .then((res) => res.json())
        .then((res) => {
          const zCollection = this.collections.get(coords.z);
          zCollection.set(
            this.coordsToString(coords.z, coords.x, coords.y),
            spacesToCollection(res["features"], coords, false)
          );
        })
        .catch((err) => {
          console.error(err);
        });
    },
    onEachFeature(feature, layer) {
      layer.on({
        mouseover: this.highlightFeature,
        mouseout: this.resetHighlight,
        click: (e) => {
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
          if (this.clickPointTarget) {
            const e2 = this.clickPointTarget;
            let obj2;
            if (e2.target.feature.properties.isSearch) {
              obj2 = this.$refs[`geoJsonSearchRef`].leafletObject;
            } else {
              obj2 = this.geoJsonObj(
                this.coordsToString(
                  e2.target.feature.properties.zoom,
                  e2.target.feature.properties.tileX,
                  e2.target.feature.properties.tileY
                )
              );
            }
            obj2.resetStyle(e2.target);
          }
          this.clickPoint = e.target.feature;
          this.clickPointTarget = e;
          this.hoverPoint = null;
          this.zoomToFeature(e.latlng, this.zoom);
          e.target.setStyle({
            weight: 5,
            color: "#222",
            fillColor: "#111",
            dashArray: "",
            fillOpacity: 0.7,
          });
        },
      });
    },
    highlightFeature(e) {
      if (
        this.clickPoint &&
        this.clickPoint.properties.id === e.target.feature.properties.id
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
      if (
        this.clickPoint &&
        this.clickPoint.properties.id === e.target.feature.properties.id
      ) {
        return;
      }
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
    zoomToFeature(latlng: LatLng, zoom: number) {
      this.map.setView(latlng, zoom);
    },
    coordsToString(z: number, x: number, y: number) {
      return `${z}-${x}-${y}`;
    },
    onCancelClickPoint() {
      this.resetHighlight;
    },
    onCenterPoint() {
      this.zoomToFeature(
        {
          lat: this.clickPoint.geometry.coordinates[1],
          lng: this.clickPoint.geometry.coordinates[0],
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
