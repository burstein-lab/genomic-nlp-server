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
      coords: coords,
      isSearch: isSearch,
      value: space.value,
    },
    geometry: {
      type: "Point",
      coordinates: [space.x, space.y],
    },
  };
};

const spaceToInfo = (point: SpaceValue): Map<string, string> => {
  let entries: Object;
  if (point.hypothetical) {
    entries = {
      Word: point.word,
      "Predicted class": point.predicted_class,
      "Trusted prediction": point.significant,
    };
  } else {
    entries = {
      Word: point.word,
      KO: point.ko,
      Label: point.label,
      Product: point.product,
      "Gene name": point.gene_name,
      "Functional category": point.predicted_class,
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

interface SpaceValue {
  word: string;
  ko: string;
  label: string;
  product: string;
  gene_name: string;
  significant: boolean;
  hypothetical: boolean;
  predicted_class: string;
  distance: string;
}

interface Space {
  id: string;
  x: number;
  y: number;
  value: SpaceValue;
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
    coords: Coords;
    isSearch: boolean;
    value: SpaceValue;
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
