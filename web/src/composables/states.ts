import { ref } from "vue";

const zoom = ref(0);
const hoverPoint = ref(null);
const clickPoint = ref(null);

export function useZoom() {
  return zoom;
}

export function useHoverPoint() {
  return hoverPoint;
}

export function useClickPoint() {
  return clickPoint;
}
