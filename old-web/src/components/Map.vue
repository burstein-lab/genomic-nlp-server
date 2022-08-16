<template>
  <div>
    <div>
      <div style="padding-top: 1vh; padding-left: 5vw">
        <searches
          @select="
            ({ spaces, latlng, zoom }) => {
              searchCollection = spacesToCollection(
                spaces,
                {
                  z: zoom,
                  x: latlng.lng,
                  y: latlng.lat,
                },
                true
              );
              zoomToFeature(latlng, zoom);
            }
          "
        />
      </div>
    </div>
    <div style="height: 97vh; width: 98vw">
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
        @ready="onMapReady(this)"
      >
        <l-tile-layer
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
  </div>
</template>

<script>
import Searches from "../components/Searches.vue";
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
    Searches,
  },
  data() {
    return {
      zoom: 0,
      controlHeader: "Information",
      publicAssetsUrl: import.meta.env.PROD
        ? "https://storage.googleapis.com/gnlp-public-assets/"
        : "/src/assets/",
      apiUrl: import.meta.env.VITE_SERVER_URL,
      getJsonOptions: {
        onEachFeature: this.onEachFeature,
      },
      controlData: null,
      collections: new Map(),
      searchCollection: this.spacesToCollection([]),
      tileSize: 1024,
    };
  },
  computed: {},
  async beforeMount() {
    const { circleMarker } = await import("leaflet/dist/leaflet-src.esm");
    // And now the Leaflet circleMarker function can be used by the options:
    this.getJsonOptions.pointToLayer = (feature, latLng) =>
      circleMarker(latLng, {
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
      axios
        .get(`${this.apiUrl}/points?z=${coords.z}&x=${coords.x}&y=${coords.y}`)
        .then((res) => {
          this.setFeatures(
            coords,
            this.spacesToCollection(res.data["features"], coords, false)
          );
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    spaceToFeature(space, coords, isSearch) {
      return {
        type: "Feature",
        properties: {
          zoom: coords.z,
          tileX: coords.x,
          tileY: coords.y,
          isSearch: isSearch,
          name: space["name"],
        },
        geometry: {
          type: "Point",
          coordinates: [space["x"], space["y"]],
        },
      };
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
    zoomToFeature(latlng, zoom) {
      this.map.setView(latlng, zoom);
    },
    setFeatures(coords, features) {
      this.collections.set(
        this.coordsToString(coords.z, coords.x, coords.y),
        features
      );
    },
    spacesToCollection(spaces, coords, isSearch) {
      const features = [];
      for (var i = 0; i < spaces.length; i++) {
        features.push(this.spaceToFeature(spaces[i], coords, isSearch));
      }
      return {
        type: "FeatureCollection",
        features: features,
      };
    },
    coordsToString(z, x, y) {
      return `${z}-${x}-${y}`;
    },
  },
  watch: {
    zoom(value) {
      // this.getFeatures();
      // this.setFeatures([]);
      console.log(value);
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
