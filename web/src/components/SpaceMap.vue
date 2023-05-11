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
      :max-zoom="maxZoom"
      :options="{
        zoomControl: false,
        wheelPxPerZoomLevel: 120,
      }"
      @ready="onMapReady()"
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
        @ready="onTileLayerReady()"
      />
      <l-geo-json
        v-for="[k, v] in collections"
        :key="`geoJson-${k}-${zoom}-${theme.global.current.dark}`"
        :ref="`geoJson-${k}-Ref`"
        :geojson="v"
        :options="geoJsonOptions"
      />
      <l-control ref="controlRef" position="topleft">
        <ControlCard
          :hoveredFeature="hoveredFeature"
          :clickedFeature="clickedLayer?.feature"
          @resetClickPoint="onResetClickPoint"
          @centerPoint="onCenterPoint"
          @setMap="onSetMap"
          @setHideMap="(shouldHideMap) => (isMapVisible = !shouldHideMap)"
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
import { useTheme } from "vuetify";
import ControlCard from "./ControlCard.vue";
import {
  SpacesResponse,
  spacesToCollection,
  Coords,
  LatLng,
  pointStyle,
  clickedPointStyle,
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
    const theme = useTheme();
    const maxZoom = Number(import.meta.env.VITE_MAX_ZOOM);
    const collections = new Map<string, any[]>();
    return {
      theme: theme,
      maxZoom: maxZoom,
      zoom: 0,
      geoJsonOptions: {
        onEachFeature: (feature: Feature, layer: any) => {},
        pointToLayer: (feature: Feature, latlng: LatLng) => {},
      },
      hoveredFeature: null as Feature | null,
      clickedLayer: null as Feature | null,
      isMapVisible: true,
      collections: collections,
      tileSize: 1024,
      map: null as LMap | null,
      searchCollectionKey: "search",
    };
  },
  async beforeMount() {
    const { circleMarker } = await import("leaflet/dist/leaflet-src.esm");
    this.geoJsonOptions.onEachFeature = this.onEachFeature;
    this.geoJsonOptions.pointToLayer = (feature: Feature, latlng: LatLng) => {
      if (this.zoom !== feature.properties.coords.z) {
        return;
      }

      if (
        this.clickedLayer?.feature?.properties?.id === feature.properties.id
      ) {
        const result = circleMarker(
          latlng,
          clickedPointStyle(feature, this.zoom, this.theme.global.current.dark)
        );
        this.clickedLayer = result;
        return result;
      }

      return circleMarker(
        latlng,
        pointStyle(feature, this.zoom, this.theme.global.current.dark)
      );
    };
  },
  methods: {
    async onSetMap(res: SpacesResponse) {
      if (!res) {
        this.collections.set(this.searchCollectionKey, spacesToCollection());
        return;
      }

      this.zoom = res.zoom;
      this.collections.set(
        this.searchCollectionKey,
        spacesToCollection(
          res.spaces,
          {
            z: res.zoom,
            x: res.latlng.lng,
            y: res.latlng.lat,
          },
          true
        )
      );
      // When both zoom and latlng change, using setView alone results in zoom change without latlng.
      await this.map.setZoom(res.zoom);
      await this.map.setView(res.latlng, res.zoom);
    },
    onTileLayerReady() {
      const tileLayer = this.$refs.tileLayerRef.leafletObject;
      tileLayer.on("tileunload", async ({ coords }: { coords: Coords }) => {
        // Either trigger cleanup, or create a set without consequences.
        this.collections.set(this.collectionID(coords), spacesToCollection());
      });
      tileLayer.on("tileloadstart", async ({ coords }: { coords: Coords }) => {
        await this.getFeatures(coords);
      });
    },
    geoJsonObj(k: string) {
      // When using v-for, ref is a list.
      const obj = this.$refs[`geoJson-${k}-Ref`];
      if (obj) return obj[0].leafletObject;
    },
    onResetClickPoint() {
      this.clickedLayer?.setStyle(
        pointStyle(
          this.clickedLayer.feature,
          this.zoom,
          this.theme.global.current.dark
        )
      );
    },
    onMapReady() {
      this.map = this.$refs.mapRef.leafletObject;
      this.map.setView(
        {
          lat: -this.tileSize / 2,
          lng: this.tileSize / 2,
        },
        0
      );
    },
    collectionID(coords: Coords): string {
      return `${coords.z}-${coords.x}-${coords.y}`;
    },
    async getFeatures(coords: Coords) {
      const id = this.collectionID(coords);
      const rawRes = await fetch(
        `map/${coords.z}/space_by_label_${coords.x}_${coords.y}.json`
      );

      if (rawRes.status === 404) return;

      const res = (await rawRes.json()) as SpacesResponse;
      this.collections.set(
        id,
        spacesToCollection(res["features"], coords, false)
      );

      const cleanup = () => {
        if (!this.collections.has(id)) return;

        if (this.zoom !== coords.z || this.collections.get(id)?.length === 0) {
          this.collections.delete(id);
          return;
        }

        setTimeout(cleanup, 3000);
      };

      setTimeout(cleanup, 3000);
    },
    // layer is the circle marker
    onEachFeature(feature: Feature, layer) {
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
    highlightFeature(layer, feature: Feature) {
      if (
        this.clickedLayer &&
        this.clickedLayer.feature.properties.id === feature.properties.id
      ) {
        return;
      }
      layer.setStyle(
        highlightedPointStyle(
          feature,
          this.zoom,
          this.theme.global.current.dark
        )
      );
      layer.bringToFront();
      this.hoveredFeature = feature;
    },
    resetHighlight(layer, feature: Feature) {
      if (
        this.clickedLayer &&
        this.clickedLayer.feature.properties.id === feature.properties.id
      ) {
        return;
      }
      layer.setStyle(
        pointStyle(feature, this.zoom, this.theme.global.current.dark)
      );
      this.hoveredFeature = null;
    },
    onClickPoint(layer, feature: Feature) {
      if (this.clickedLayer) {
        this.clickedLayer.setStyle(
          pointStyle(
            this.clickedLayer.feature,
            this.zoom,
            this.theme.global.current.dark
          )
        );
      }

      this.clickedLayer = layer;
      this.hoveredFeature = null;
      this.onCenterPoint();
      this.clickedLayer.setStyle(
        clickedPointStyle(
          this.clickedLayer.feature,
          this.zoom,
          this.theme.global.current.dark
        )
      );
    },
    onCenterPoint() {
      this.map?.setView(
        {
          lat: this.clickedLayer.feature.geometry.coordinates[1],
          lng: this.clickedLayer.feature.geometry.coordinates[0],
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
