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

const unselectedPointStyle = (zoom: number, feature: Feature) => ({
  radius: zoom + 2,
  fillColor: feature.properties.value.color, // TODO: border color by feature.properties.isSearch ? "#007800" : "#ff7800",
  weight: 1,
  opacity: 1,
  fillOpacity: 0.8,
});

const selectedPointStyle = (zoom: number, feature: Feature) => ({
  weight: 5,
  color: "#222",
  fillColor: feature.properties.value.color,
  dashArray: "",
  fillOpacity: 0.7,
});

const highlightedPointStyle = {
  weight: 5,
  color: "#666",
  dashArray: "",
  fillOpacity: 0.7,
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
  if (point.value.hypothetical) {
    return `
      Word: ${point.value.word}<br />
      Predicted class: ${point.value.predicted_class} <br />
      Trusted prediction: ${point.value.significant}<br />
    `;
  }

  return `
    Word: ${point.value.word}<br />
    KO: ${point.value.ko}<br />
    Label: ${point.value.label}<br />
    Product: ${point.value.product}<br />
    Gene name: ${point.value.gene_name}<br />
    Functional category: ${point.value.predicted_class} <br />
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
export {
  spacesToCollection,
  spaceToInfo,
  searchSpaces,
  unselectedPointStyle,
  selectedPointStyle,
  highlightedPointStyle,
};
