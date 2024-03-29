const searchType = (
  label: string,
  type: string,
  emit?: string,
  multiple: boolean = false
): SearchType => ({
  label,
  type: type,
  emit: emit ? emit : type,
  multiple,
});

interface SearchType {
  label: string;
  type: string;
  emit: string;
  multiple: boolean;
}

const searchModeToType = {
  "KEGG ortholog": searchType("KEGG ortholog", "space"),
  "Functional category": searchType("Functional category", "label"),
  "Gene description": searchType("Gene description", "gene_product"),
  "Gene name": searchType("Gene name", "gene"),
  Neighbors: searchType("Model word", "neighbors"),
  "Model word": searchType("Model word", "word", "word", true),
} as { [key: string]: SearchType };

const pointStyle = (
  space: Space,
  isSearch: boolean,
  zoom: number,
  isDarkTheme: boolean
) => {
  return {
    radius: zoom + (isSearch ? 3 : 2),
    color: isSearch ? (isDarkTheme ? "#FFFFFF" : "#000000") : "#666",
    fillColor: space.value.color,
    weight: isSearch ? 2 : 1,
    opacity: 1,
    fillOpacity: 0.7,
  };
};

const highlightedPointStyle = (
  space: Space,
  isSearch: boolean,
  zoom: number,
  isDarkTheme: boolean
) => {
  const res = pointStyle(space, isSearch, zoom, isDarkTheme);
  res.radius += isSearch ? 1 : 2;
  res.weight += isSearch ? 1 : 2;
  res.color = isDarkTheme ? "#FFFFFF" : "#000000";
  return res;
};

const spaceToInfo = (point: SpaceValue): Map<string, string> => {
  let entries: Object;
  if (point.hypothetical) {
    entries = {
      Word: point.word,
      "Predicted class": point.predicted_class,
      "Prediction confidence": point.significant ? "high" : "low",
      "NCBI NR description": point.ncbi_nr,
      "Gene count in family": point.word_count,
    };
  } else {
    entries = {
      Word: point.word,
      "KEGG Orthology": point.ko,
      Product: point.product,
      "Gene name": point.gene_name,
      "Functional category": point.predicted_class,
      "Gene count in family": point.word_count,
      "KEGG information": kosWithoutLink.includes(point.ko)
        ? "N/A"
        : "https://www.genome.jp/entry/" + point.ko,
    };
  }

  return new Map(Object.entries(entries));
};

const kosWithoutLink = ["CRISPR", "tRNA", "rRNA", "tmRNA"];

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
  product: string;
  gene_name: string;
  significant: boolean;
  hypothetical: boolean;
  predicted_class: string;
  ncbi_nr: string;
  distance: string;
  color: string;
  word_count: number;
  tax_distribution: [string, number][];
  tax_ratio: number;
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

interface ScatterData {
  label: string;
  data: { x: number; y: number }[];
  ticks: string[];
}

const searchSpaces = async (
  type: string,
  e: string[],
  signal
): Promise<SpacesResponse> => {
  const url = new URL(
    `${import.meta.env.VITE_SERVER_URL}/${type}/get/${encodeURIComponent(
      e.toString()
    )}`
  );
  const rawRes = await fetch(url.href, { signal });
  return await rawRes.json();
};

export type {
  Coords,
  Space,
  LatLng,
  SpacesResponse,
  ScatterData,
  SpaceValue,
  SearchType,
};
export {
  spaceToInfo,
  searchSpaces,
  pointStyle,
  highlightedPointStyle,
  searchModeToType,
};
