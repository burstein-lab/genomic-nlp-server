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
}

interface Space {
  name: string;
  x: number;
  y: number;
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
    zoom: number;
    tileX: number;
    tileY: number;
    isSearch: boolean;
    name: string;
  };
  geometry: {
    type: string;
    coordinates: number[];
  };
}
