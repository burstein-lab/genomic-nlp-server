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
      <l-circle-marker
        v-if="clickedSpace"
        ref="clickedSpaceLayerRef"
        :lat-lng="[clickedSpace.y, clickedSpace.x]"
        :radius="zoom + 4"
        :color="theme.global.current.dark ? '#FFFFFF' : '#000000'"
        :fillColor="clickedSpace.value.color"
        :weight="3"
        :opacity="1"
        :fillOpacity="0.7"
        @ready="(e) => e.bringToFront()"
      />
      <l-circle-marker
        v-for="[_, space] in searchSpaces"
        :lat-lng="[space.y, space.x]"
        :radius="zoom + 3"
        :color="theme.global.current.dark ? '#FFFFFF' : '#000000'"
        :fillColor="space.value.color"
        :weight="2"
        :opacity="1"
        :fillOpacity="0.7"
        @mouseover="(e) => onMouseOver(e, space)"
        @mouseout="(e) => onMouseOut(e, space)"
        @click="(e) => onClick(e, space)"
      />
      <l-circle-marker
        v-for="space in backgroundInteractiveSpaces(zoom)"
        :lat-lng="[space.y, space.x]"
        :radius="zoom + 2"
        color="#666"
        :fillColor="space.value.color"
        :weight="1"
        :opacity="1"
        :fillOpacity="0.7"
        @mouseover="(e) => onMouseOver(e, space)"
        @mouseout="(e) => onMouseOut(e, space)"
        @click="(e) => onClick(e, space)"
      />
      <l-control ref="controlRef" position="topleft">
        <ControlCard
          :hoveredSpace="hoveredSpace"
          :clickedSpace="clickedSpace"
          :isDiamondLoading="isDiamondLoading"
          @setClickPoint="onSetClickPoint"
          @setDiamondLoading="onSetDiamondLoading"
          @resetCoords="
            async () => {
              zoom = 0;
              await map.setZoom(zoom);
              await map.setView(
                {
                  lat: -tileSize / 2,
                  lng: tileSize / 2,
                },
                zoom
              );
            }
          "
          @resetClickPoint="onResetClickPoint"
          @centerPoint="onCenterPoint"
          @setMap="onSetSearchSpaces"
          @setHideMap="(shouldHideMap) => (isMapVisible = !shouldHideMap)"
        />
      </l-control>
    </l-map>
  </div>
  <v-dialog v-model="diamondDialog" width="800">
    <v-card>
      <v-card-text>
        Selecting a space during sequence search will abort the search.
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="info"
          variant="text"
          @click="diamondDialogSelection = null"
        >
          Cancel selection
        </v-btn>
        <v-btn
          color="error"
          variant="text"
          @click="
            isDiamondLoading = false;
            clickedSpace = diamondDialogSelection;
            diamondDialogSelection = null;
          "
        >
          Cancel search
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import {
  LMap,
  LTileLayer,
  LControl,
  LControlZoom,
  LCircleMarker,
} from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import { useTheme } from "vuetify";
import ControlCard from "./ControlCard.vue";
import {
  searchModeToType,
  SpacesResponse,
  Coords,
  searchSpaces,
  Space,
  pointStyle,
  highlightedPointStyle,
} from "@/composables/spaces";

export default {
  name: "SpaceMap",
  components: {
    LMap,
    LCircleMarker,
    LControlZoom,
    LTileLayer,
    LControl,
    ControlCard,
  },
  data() {
    const theme = useTheme();
    const maxZoom = Number(import.meta.env.VITE_MAX_ZOOM);
    return {
      theme: theme,
      maxZoom: maxZoom,
      zoom: 0,
      hoveredSpace: null as Space | null,
      _clickedSpace: undefined as Space | null,
      isMapVisible: true,
      tileToSpaces: new Map<string, Space[]>(),
      tileSize: 1024,
      publicURL: import.meta.env.VITE_PUBLIC_URL,
      map: null as LMap | null,
      searchSpaces: new Map<string, Space>(),
      isDiamondLoading: false,
      diamondDialogSelection: null as Space | null,
    };
  },
  methods: {
    async onSetDiamondLoading(isDiamondLoading: boolean) {
      this.isDiamondLoading = isDiamondLoading;
      if (isDiamondLoading) {
        this._clickedSpace = null;
      }
    },
    async onSetClickPoint(word: string, setQueryParams = true) {
      const res = await searchSpaces(
        "word",
        word,
        new AbortController().signal
      );
      if (setQueryParams) {
        this.clickedSpace = res.spaces[0];
      } else {
        this._clickedSpace = res.spaces[0];
      }
      this.focusSpaceResponse(res);
    },
    async onSetSearchSpaces(res: SpacesResponse, autoClick = true) {
      this.searchSpaces.clear();

      for (const space of res.spaces as Space[]) {
        this.searchSpaces.set(space.value.word, space);
      }

      if (autoClick && res.spaces.length === 1) {
        this.clickedSpace = res.spaces[0];
      }

      console.log(res.zoom, res.latlng);
      this.focusSpaceResponse(res);
    },
    focusSpaceResponse(res: SpacesResponse) {
      this.zoom = res.zoom;
      // When both zoom and latlng change, using setView alone results in zoom change without latlng.
      this.map.setZoom(res.zoom);
      this.map.setView(res.latlng, res.zoom);
    },
    onTileLayerReady() {
      const tileLayer = this.$refs.tileLayerRef.leafletObject;
      tileLayer.on("tileloadstart", async ({ coords }: { coords: Coords }) => {
        await this.getInteractiveSpaces(coords);
      });
    },
    onResetClickPoint() {
      this.clickedSpace = null;
    },
    async onMapReady() {
      let zoom = 0;
      let lat = -this.tileSize / 2;
      let lng = this.tileSize / 2;
      this.map = this.$refs.mapRef.leafletObject;
      if (this.$route.query.location) {
        [zoom, lat, lng] = this.$route.query.location.split(",");
      }

      this.map.setView(
        {
          lat: lat,
          lng: lng,
        },
        zoom
      );

      // Setting before search spaces in case the clicked space is in the search results.
      if (this.$route.query.clickedSpace) {
        this.onSetClickPoint(this.$route.query.clickedSpace, false);
      } else {
        this.clickedSpace = null;
      }

      if (this.$route.query.searchValue) {
        const res = await searchSpaces(
          searchModeToType[this.$route.query.searchMode].type,
          this.$route.query.searchValue
        );
        await this.onSetSearchSpaces(res, false);
      }
    },
    coordsToTile(coords: Coords) {
      return `${coords.z}_${coords.x}_${coords.y}`;
    },
    async getInteractiveSpaces(coords: Coords) {
      const rawRes = await fetch(
        `${this.publicURL}map/${coords.z}/space_by_label_${coords.x}_${coords.y}.json`
      );

      if (rawRes.status === 404) return;

      const res = (await rawRes.json()) as SpacesResponse;

      this.tileToSpaces.set(this.coordsToTile(coords), res.spaces as Space[]);

      const cleanup = () => {
        if (!this.tileToSpaces.has(this.coordsToTile(coords))) return;

        if (
          this.zoom !== coords.z ||
          this.tileToSpaces.get(this.coordsToTile(coords))?.length === 0
        ) {
          this.tileToSpaces.delete(this.coordsToTile(coords));
          return;
        }

        setTimeout(cleanup, 3000);
      };

      setTimeout(cleanup, 3000);
    },
    onCenterPoint() {
      this.map?.setView(
        {
          lat: this.clickedSpace.y,
          lng: this.clickedSpace.x,
        },
        this.zoom
      );
    },
    onMouseOver(e, space: Space) {
      if (space.value.word === this.clickedSpace?.value?.word) return;

      e.target.bringToFront();
      e.target.setStyle(
        highlightedPointStyle(
          space,
          this.searchSpaces.has(space.value.word),
          this.zoom,
          this.theme.global.current.dark
        )
      );
      this.hoveredSpace = space;
    },
    onMouseOut(e, space: Space) {
      e.target.setStyle(
        pointStyle(
          space,
          this.searchSpaces.has(space.value.word),
          this.zoom,
          this.theme.global.current.dark
        )
      );
      this.hoveredSpace = null;
      if (this.$refs.clickedSpaceLayerRef?.leafletObject)
        this.$refs.clickedSpaceLayerRef?.leafletObject.bringToFront();
    },
    onClick(e, space: Space) {
      this.clickedSpace = space;
      this.hoveredSpace = null;
      this.onCenterPoint();
    },
    backgroundInteractiveSpaces(zoom: number) {
      if (!this.isMapVisible) return [];

      const res: Space[] = [];
      for (const [tile, spaces] of this.tileToSpaces) {
        if (tile[0] !== String(zoom)) continue;

        for (const space of spaces) {
          if (
            !this.searchSpaces.has(space.value.word) &&
            this.clickedSpace?.value.word !== space.value.word
          ) {
            res.push(space);
          }
        }
      }
      return res;
    },
  },
  computed: {
    clickedSpace: {
      get() {
        return this._clickedSpace;
      },
      set(value: Space | null) {
        if (this.isDiamondLoading) {
          this.diamondDialogSelection = value;
          return;
        }

        this._clickedSpace = value;
        this.$router.push({
          query: {
            ...this.$route.query,
            clickedSpace: value ? value.value.word : "",
          },
        });
      },
    },
    diamondDialog(): boolean {
      return Boolean(this.diamondDialogSelection);
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
