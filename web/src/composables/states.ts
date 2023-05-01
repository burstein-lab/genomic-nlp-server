import { ref } from "vue";

const hoverPoint = ref(null);
const clickedCircle = ref(null);

export function useHoverPoint() {
  return hoverPoint;
}

export function useClickedCircle() {
  return clickedCircle;
}
