const spacesToCollection = (
  spaces?: Space[],
  coords?: Coords,
  isSearch?: boolean
): FeatureCollection => {
  const features: Feature[] = [];
  if (spaces !== undefined && coords !== undefined && isSearch !== undefined) {
    for (var i = 0; i < spaces.length; i++) {
      features.push(spaceToFeature(spaces[i], coords, isSearch));
    }
  }

  return {
    type: "FeatureCollection",
    features: features,
  };
};

const pointStyle = (feature: Feature, zoom: number, isDarkTheme: boolean) => {
  return {
    radius: zoom + 2,
    color: feature.properties.isSearch
      ? isDarkTheme
        ? "#FFFFFF"
        : "#000000"
      : "#666",
    fillColor: feature.properties.value.color,
    weight: 1,
    opacity: 1,
    fillOpacity: 0.7,
  };
};

const highlightedPointStyle = (
  feature: Feature,
  zoom: number,
  isDarkTheme: boolean
) => {
  const res = pointStyle(feature, zoom, isDarkTheme);
  res.radius += 2;
  res.weight += 2;
  res.color = isDarkTheme ? "#FFFFFF" : "#000000";
  return res;
};

const clickedPointStyle = (
  feature: Feature,
  zoom: number,
  isDarkTheme: boolean
) => {
  const res = highlightedPointStyle(feature, zoom, isDarkTheme);
  return res;
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

const spaceToInfo = (point: Space): Map<string, string> => {
  let entries: Object;
  if (point.value.hypothetical) {
    entries = {
      Word: point.value.word,
      "Predicted class": point.value.predicted_class,
      "Trusted prediction": point.value.significant,
    };
  } else {
    entries = {
      Word: point.value.word,
      KO: point.value.ko,
      Label: point.value.label,
      Product: point.value.product,
      "Gene name": point.value.gene_name,
      "Functional category": point.value.predicted_class,
    };
  }

  return new Map(Object.entries(entries));
};

interface LatLng {
  lat: number;
  lng: number;
}

interface SpacesResponse {
  spaces: Space[];
  latlng: LatLng;
  zoom: Number;
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
    significant: boolean;
    hypothetical: boolean;
    predicted_class: string;
    distance: string;
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

interface ScatterData {
  label: string;
  data: { x: number; y: number }[];
  ticks: string[];
}

const searchSpaces = async (type: string, e: string[], signal) => {
  console.log(`${import.meta.env.VITE_SERVER_URL}/${type}/get/${e.toString()}`);
  const url = new URL(
    `${import.meta.env.VITE_SERVER_URL}/${type}/get/${e.toString()}`
  );
  const rawRes = await fetch(url.href, { signal });
  return await rawRes.json();
};

export type {
  Coords,
  Space,
  Feature,
  FeatureCollection,
  LatLng,
  SpacesResponse,
  ScatterData,
};
export {
  spacesToCollection,
  spaceToInfo,
  searchSpaces,
  pointStyle,
  clickedPointStyle,
  highlightedPointStyle,
};
