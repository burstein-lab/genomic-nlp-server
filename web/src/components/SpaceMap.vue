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
        :url="`${publicURL}map/{z}/space_by_label_{x}_{y}.png`"
        layer-type="base"
        name="OpenStreetMap"
        :max-zoom="maxZoom"
        :min-zoom="0"
        :tileSize="tileSize"
        @ready="onTileLayerReady()"
      />
      <l-geo-json
        v-if="clickedFeature"
        :key="`geoJson-clickerFeature-${zoom}-${theme.global.current.dark}-${renderGeoJsonsToggle}`"
        :geojson="{
          type: 'FeatureCollection',
          features: [clickedFeature],
        }"
        :options="geoJsonClickedOptions"
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
          :clickedFeature="clickedFeature"
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
  searchModeToType,
  FeatureCollection,
  SpacesResponse,
  spacesToCollection,
  Coords,
  spaceToFeature,
  searchSpaces,
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
    const collections = new Map<string, FeatureCollection>();
    return {
      theme: theme,
      maxZoom: maxZoom,
      zoom: 0,
      geoJsonOptions: {
        onEachFeature: (feature: Feature, layer: any) => {},
        pointToLayer: (feature: Feature, latlng: LatLng) => {},
      },
      geoJsonClickedOptions: {
        pointToLayer: (feature: Feature, latlng: LatLng) => {},
      },
      hoveredFeature: null as Feature | null,
      _clickedFeature: undefined as Feature | null,
      isMapVisible: true,
      collections: collections,
      tileSize: 1024,
      publicURL: import.meta.env.VITE_PUBLIC_URL,
      map: null as LMap | null,
      renderGeoJsonsToggle: false, // Used to force a re-render of the map
      searchCollectionKey: "search",
      circleMarker: (latlng: LatLng, layer: Object): LCircleMarker => {},
      clickedLayer: null as LCircleMarker | null,
    };
  },
  async beforeMount() {
    const { circleMarker } = await import("leaflet/dist/leaflet-src.esm");
    this.circleMarker = circleMarker;
    this.geoJsonOptions.onEachFeature = this.onEachFeature;
    this.geoJsonOptions.pointToLayer = (feature: Feature, latlng: LatLng) => {
      if (
        this.clickedFeature?.properties?.value?.word ===
        feature.properties.value.word
      ) {
        this.clickedFeature = feature;
        return null;
      }

      if (!feature.properties.isSearch) {
        if (this.zoom !== feature.properties.coords.z) return null;

        const searchFeature = this.collections
          .get(this.searchCollectionKey)
          ?.features?.find(
            (f: Feature) => f.properties.id === feature.properties.id
          );
        if (searchFeature) {
          return null;
        }
      }

      return circleMarker(
        latlng,
        pointStyle(feature, this.zoom, this.theme.global.current.dark)
      );
    };
    this.geoJsonClickedOptions.pointToLayer = (
      feature: Feature,
      latlng: LatLng
    ) => {
      this.clickedLayer = circleMarker(
        latlng,
        clickedPointStyle(feature, this.zoom, this.theme.global.current.dark)
      );
      this.clickedLayer.bringToFront();
      return this.clickedLayer;
    };

    // Setting before search spaces in case the clicked feature is in the search results.
    if (this.$route.query.clickedFeature) {
      const spaces = await searchSpaces(
        "word",
        this.$route.query.clickedFeature,
        new AbortController().signal
      );
      this.clickedFeature = spaceToFeature(spaces.spaces[0]);
    } else {
      this.clickedFeature = null;
    }

    if (this.$route.query.searchValue) {
      const spaces = await searchSpaces(
        searchModeToType[this.$route.query.searchMode].type,
        this.$route.query.searchValue
      );
      await this.onSetMap(spaces, false);
    }
  },
  methods: {
    async onSetMap(res: SpacesResponse, focus = true) {
      if (!res) {
        this.collections.set(this.searchCollectionKey, spacesToCollection());
        return;
      }

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

      if (focus) {
        this.zoom = res.zoom;
        // When both zoom and latlng change, using setView alone results in zoom change without latlng.
        await this.map.setZoom(res.zoom);
        await this.map.setView(res.latlng, res.zoom);
      }

      this.renderGeoJsonsToggle = !this.renderGeoJsonsToggle;
    },
    onTileLayerReady() {
      const tileLayer = this.$refs.tileLayerRef.leafletObject;
      tileLayer.on("tileunload", async ({ coords }: { coords: Coords }) => {
        // Either trigger cleanup, or create a set without consequences.
        // this.collections.set(this.collectionID(coords), spacesToCollection());
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
      this.clickedFeature = null;
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
        `${this.publicURL}map/${coords.z}/space_by_label_${coords.x}_${coords.y}.json`
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
          this.onClickPoint(feature);
        },
      });
    },
    highlightFeature(layer, feature: Feature) {
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
      layer.setStyle(
        pointStyle(feature, this.zoom, this.theme.global.current.dark)
      );
      this.hoveredFeature = null;
      this.clickedLayer?.bringToFront();
    },
    async onClickPoint(feature: Feature) {
      if (this.clickedFeature?.properties?.coords) {
        const id = this.clickedFeature.properties.isSearch
          ? this.searchCollectionKey
          : this.collectionID(this.clickedFeature.properties.coords);
        this.collections.get(id)?.features.push(this.clickedFeature);

        const marker = this.circleMarker(
          {
            lat: this.clickedFeature.geometry.coordinates[1],
            lng: this.clickedFeature.geometry.coordinates[0],
          },
          pointStyle(
            this.clickedFeature,
            this.zoom,
            this.theme.global.current.dark
          )
        );
        this.onEachFeature(this.clickedFeature, marker);
        this.geoJsonObj(id)?.addLayer(marker);
      }

      const id = feature.isSearch
        ? this.searchCollectionKey
        : this.collectionID(feature.properties.coords);

      if (this.collections.has(id)) {
        const index = this.collections
          .get(id)
          ?.features.findIndex(
            (f: Feature) => f.properties.id === feature.properties.id
          );
        this.collections.get(id)?.features.splice(index, 1);
      }

      this.clickedFeature = feature;
      this.hoveredFeature = null;
      this.onCenterPoint();
    },
    onCenterPoint() {
      this.map?.setView(
        {
          lat: this.clickedFeature.geometry.coordinates[1],
          lng: this.clickedFeature.geometry.coordinates[0],
        },
        this.zoom
      );
    },
  },
  computed: {
    clickedFeature: {
      get() {
        return this._clickedFeature;
      },
      set(value: Feature | null) {
        this._clickedFeature = value;
        this.$router.push({
          query: {
            ...this.$route.query,
            clickedFeature: value ? value.properties.value.word : "",
          },
        });
      },
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
