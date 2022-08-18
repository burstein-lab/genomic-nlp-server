export const useZoom = () => useState<number>("zoom", () => 0);
export const useShouldShowMap = () => useState<boolean>("show-map", () => true);
export const useLatLng = () =>
  useState<{ lat: number; lng: number }>("latlng", () => {
    return { lat: 0, lng: 0 };
  });
