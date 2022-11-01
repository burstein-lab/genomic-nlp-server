export function spacesToCollection(
  spaces: Space[],
  coords: Coords,
  isSearch: boolean
): FeatureCollection {
  const features: Feature[] = [];
  for (var i = 0; i < spaces.length; i++) {
    features.push(spaceToFeature(spaces[i], coords, isSearch));
  }
  return {
    type: "FeatureCollection",
    features: features,
  };
}

function spaceToFeature(
  space: Space,
  coords: Coords,
  isSearch: boolean
): Feature {
  return {
    type: "Feature",
    properties: {
      id: space.id,
      zoom: coords.z,
      tileX: coords.x,
      tileY: coords.y,
      isSearch: isSearch,
      value: space.value,
    },
    geometry: {
      type: "Point",
      coordinates: [space["x"], space["y"]],
    },
  };
}

interface Space {
  id: string;
  x: number;
  y: number;
  value: string;
}

interface Coords {
  x: number;
  y: number;
  z: number;
}

export interface FeatureCollection {
  type: "FeatureCollection";
  features: Feature[];
}

export interface Feature {
  type: "Feature";
  properties: {
    id: number;
    zoom: number;
    tileX: number;
    tileY: number;
    isSearch: boolean;
    value: Object;
  };
  geometry: {
    type: string;
    coordinates: number[];
  };
}
