const spacesToCollection = (
  spaces: Space[],
  coords: Coords,
  isSearch: boolean
): FeatureCollection => {
  const features: Feature[] = [];
  for (var i = 0; i < spaces.length; i++) {
    features.push(spaceToFeature(spaces[i], coords, isSearch));
  }
  console.log(features);
  return {
    type: "FeatureCollection",
    features: features,
  };
};

const spaceToFeature = (
  space: Space,
  coords: Coords,
  isSearch: boolean
): Feature => {
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
      coordinates: [space.y, space.x],
    },
  };
};

interface LatLng {
  lat: number;
  lng: number;
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

interface FeatureCollection {
  type: "FeatureCollection";
  features: Feature[];
}

interface Feature {
  type: "Feature";
  properties: {
    id: string;
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

export type { Coords, Space, Feature, FeatureCollection, LatLng };
export { spacesToCollection };
