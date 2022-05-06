<template>
  <div style="height: 75vh; width: 50vw">
    <l-map
      ref="mapRef"
      v-model="zoom"
      v-model:zoom="zoom"
      crs="Simple"
      @ready="onMapReady()"
    >
      <l-image-overlay
        url="/src/assets/space_by_label.png"
        :bounds="[
          [-200, -200],
          [200, 200],
        ]"
      >
      </l-image-overlay>
      <l-geo-json
        ref="geoJsonRef"
        :geojson="features"
        :options="geojsonOptions"
        @ready="onGeoJsonReady()"
      />
      <l-control ref="controlRef">
        <div class="info">
          <h4 v-html="controlHeader"></h4>
          <div
            v-html="
              controlData !== null
                ? 'point id <b>' + controlData.name + '</b>'
                : 'Hover over a point'
            "
          ></div>
        </div>
      </l-control>
    </l-map>
  </div>
  <button @click="calcFeatures">Add 1</button>
</template>

<script>
import {
  LMap,
  LIcon,
  LTileLayer,
  LMarker,
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
import axios from "axios";

export default {
  components: {
    LMap,
    LIcon,
    LTileLayer,
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
      zoom: 3,
      controlHeader: "Information",
      apiUrl: import.meta.env.VITE_SERVER_URL,
      geojsonOptions: {
        onEachFeature: this.onEachFeature,
      },
      controlData: null,
      features: {
        type: "FeatureCollection",
        features: [],
      },
    };
  },
  computed: {},
  async beforeMount() {
    const { circleMarker } = await import("leaflet/dist/leaflet-src.esm");
    // And now the Leaflet circleMarker function can be used by the options:
    this.geojsonOptions.pointToLayer = (feature, latLng) =>
      circleMarker(latLng, {
        radius: this.zoom * 2,
        fillColor: "#ff7800",
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8,
      });
  },
  mounted() {
    this.$nextTick(() => {
      // this.$refs.mapRef.leafletObject.fitBounds([[0, 0], [1000, 1000]]);
    });
  },
  methods: {
    onGeoJsonReady() {
      this.geoJson = this.$refs.geoJsonRef.leafletObject;
    },
    onMapReady() {
      this.map = this.$refs.mapRef.leafletObject;
    },
    calcFeatures() {
      axios
        .get(this.apiUrl + "/points")
        .then((res) => {
          const features = [];
          console.log(res.data.length);
          for (var i = 0; i < res.data.length; i++) {
            const d = res.data[i];
            features.push({
              type: "Feature",
              properties: {
                name: d["name"],
              },
              geometry: {
                type: "Point",
                coordinates: [d["x"], d["y"]],
              },
            });
          }
          // this.features["features"] = features;
          this.features = {
            type: "FeatureCollection",
            features: features,
          };
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
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
        click: this.zoomToFeature,
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
      this.geoJson.resetStyle(e.target);
      this.controlData = null;
    },
    zoomToFeature(e) {
      // TODO fix or remove
      this.map.fitBounds(e.target.getBounds());
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
</style>
