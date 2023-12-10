import { reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

import { Space } from "@/composables/spaces";

const route = useRoute();

const queryParams = reactive({
  clickedSpace: undefined as string | undefined,
  plot: undefined as string | undefined,
  searchMode: route.query.searchMode
    ? route.query.searchMode
    : ("" as string | undefined),
  searchValue: route.query.searchValue as string | string[] | undefined,
  location: { zoom: 0, lat: 0, lng: 0 } as {
    zoom: number;
    lat: number;
    lng: number;
  },
});

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

export { queryParams, pushQueryParams };
