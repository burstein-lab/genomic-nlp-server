import { ref } from "vue";

const zoom = ref(0);
const showMap = ref(true);
const latlng = ref({ lat: 0, lng: 0 });
const hoverPoint = ref(null);
const clickPoint = ref(null);

export function useZoom() {
  return zoom;
}
export function useShouldShowMap() {
  return showMap;
}

export function useLatLng() {
  return latlng;
}

export function useHoverPoint() {
  return hoverPoint;
}

export function useClickPoint() {
  return clickPoint;
}
