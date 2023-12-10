import { reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();

const queryParams = reactive({
  clickedSpace: undefined as string | undefined,
  plot: undefined as string | undefined,
  searchMode: undefined as string | undefined,
  searchValue: undefined as string | undefined,
  location: { zoom: 0, lat: 0, lng: 0 } as {
    zoom: number;
    lat: number;
    lng: number;
  },
});

const setQueryParams = () => {
  const route = useRoute();
  queryParams.clickedSpace = route.query.clickedSpace as string | undefined;
  queryParams.plot = route.query.plot as string | undefined;
  queryParams.searchMode = route.query.searchMode as string | undefined;
  queryParams.searchValue = route.query.searchValue as string | undefined;
  const location = route.query.location as string | undefined;
  if (location) {
    const [zoom, lat, lng] = location.split(",");
    queryParams.location = {
      zoom: parseInt(zoom),
      lat: parseFloat(lat),
      lng: parseFloat(lng),
    };
  }
};

const pushQueryParams = async () => {
  const router = useRouter();
  await router.push({
    query: {
      clickedSpace: queryParams.clickedSpace,
      location: `${queryParams.location.zoom},${queryParams.location.lat},${queryParams.location.lng}`,
      plot: queryParams.plot,
      searchMode: queryParams.searchMode,
      searchValue: queryParams.searchValue,
    },
  });
};

export { queryParams, setQueryParams, pushQueryParams };
