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
          <control-card
            :info="
              controlData !== null
                ? 'Point id <b>' + controlData.name + '</b>'
                : 'Hover over a point'
            "
            @select="onSelect"
          />
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
  },
  data() {
    return {
      latlng: useLatLng(),
      zoom: useZoom(),
      publicAssetsUrl: "/",
      apiUrl: "http://127.0.0.1:5000/",
      getJsonOptions: {
        onEachFeature: this.onEachFeature,
      },
      controlData: null,
      isMapVisible: useShouldShowMap(),
      collections: new Map(),
      tileSize: 1024,
      searchCollection: null,
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
        click: (e) => this.zoomToFeature(e.latlng, this.zoom),
      });
    },
    highlightFeature(e) {
      const layer = e.target;
      layer.setStyle({
        weight: 5,
        color: "#666",
        dashArray: "",
        fillOpacity: 0.7,
      });
      layer.bringToFront();
      this.controlData = layer.feature.properties;
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
      this.controlData = null;
    },
    zoomToFeature(latlng, zoom: number) {
      this.map.setView(latlng, zoom);
    },
    coordsToString(z: number, x: number, y: number) {
      return `${z}-${x}-${y}`;
    },
    onSelect(type: string, e: string[]) {
      const runtimeConfig = useRuntimeConfig();
      fetch(`${runtimeConfig.public.apiBase}/${type}/get/${e.toString()}`)
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
        });
    },
  },
  watch: {
    zoom(value: number) {
      console.log(value);
    },
    searchCollection(value) {
      this.zoomToFeature(this.latlng, this.zoom);
      return value;
    },
  },
};
</script>

<style>
.info {
  padding: 6px 8px;
  font: 14px/16px Arial, Helvetica, sans-serif;
  background: white;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
  border-radius: 5px;
}
.info h4 {
  margin: 0 0 5px;
  color: #777;
}

.leaflet-pane {
  z-index: 1;
}

#mapRef {
  background: white;
}
</style>
