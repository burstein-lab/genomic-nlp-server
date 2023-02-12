const spacesToCollection = (
  spaces: Space[],
  coords: Coords,
  isSearch: boolean
): FeatureCollection => {
  const features: Feature[] = [];
  for (var i = 0; i < spaces.length; i++) {
    features.push(spaceToFeature(spaces[i], coords, isSearch));
  }
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
      coordinates: [space.x, space.y],
    },
  };
};

const spaceToInfo = (point: Space): string => {
  return `
          Word: ${point.value.word} <br />
          KO: ${point.value.ko} <br />
          Label: ${point.value.label} <br />
          Product: ${point.value.product} <br />
          Gene Name: ${point.value.gene_name} <br />
          Significant: ${point.value.significant} <br />
          Predicted Class: ${point.value.predicted_class} <br />
          `;
};

interface LatLng {
  lat: number;
  lng: number;
}

interface Space {
  id: string;
  x: number;
  y: number;
  value: {
    word: string;
    ko: string;
    label: string;
    product: string;
    gene_name: string;
    significant: string;
    predicted_class: string;
  };
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

const searchSpaces = async (type: string, e: string[], k?: number) => {
  const url = new URL(
    `${import.meta.env.VITE_SERVER_URL}/${type}/get/${e.toString()}`
  );
  if (type === "neighbors" && k) {
    url.searchParams.append("k", k.toString());
  }
  const rawRes = await fetch(url.href);
  return await rawRes.json();
};

export type { Coords, Space, Feature, FeatureCollection, LatLng };
export { spacesToCollection, spaceToInfo, searchSpaces };
