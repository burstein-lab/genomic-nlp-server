<template>
  <v-radio-group inline v-model="fromSequence" hide-details class="py-1">
    <v-radio label="Text" :value="true"></v-radio>
    <v-radio label="File" :value="false"></v-radio>
  </v-radio-group>
  <v-textarea
    v-if="fromSequence"
    v-model="sequence"
    filled
    auto-grow
    label="Search by sequence"
    rows="3"
    row-height="30"
    shaped
    :append-icon="loading ? 'mdi-close' : 'mdi-send'"
    @click:append="loading ? onCancelSearch() : onSequenceSearch(sequence)"
    density="comfortable"
    hide-details
  />
  <v-file-input
    v-else
    show-size
    density="comfortable"
    v-model="sequenceFile"
    label="Upload file"
    hide-details
  />
  <v-container
    v-if="downloadableDiamondResult !== null && !loading"
    class="ps-0 pe-0 pb-0"
  >
    <v-row>
      <v-col cols="11">
        <v-alert
          v-if="downloadableDiamondResult === ''"
          icon="mdi-alert-outline"
          color="error"
          density="compact"
          text="No significat hit was found in the DB."
        ></v-alert>
        <v-btn v-else @click="downloadDiamondResult" color="info">
          Download diamond result
        </v-btn>
      </v-col>
      <v-col cols="1"></v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { searchSpaces } from "@/composables/spaces";

export default {
  name: "DiamondSearch",
  data: () => {
    return {
      fromSequence: true,
      loading: false,
      plotToggle: "",
      scatterData: null as Object | null,
      scatterOptions: null as Object | null,
      diamondUrl: new URL(`${import.meta.env.VITE_DIAMOND_URL}`),
      serverUrl: new URL(import.meta.env.VITE_SERVER_URL),
      sequenceFile: new Array(),
      sequence: "",
      shouldShowMap: true,
      apiUrl: import.meta.env.VITE_SERVER_URL,
      downloadableDiamondResult: null as string | null,
      controller: new AbortController(),
    };
  },
  beforeMount() {
    if (this.$route.query.searchValue) {
      this.sequence = this.$route.query.searchValue;
      this.onSequenceSearch(this.sequence);
    }
  },
  emits: ["setMap", "setLoading"],
  methods: {
    onCancelSearch() {
      this.controller.abort();
      this.controller = new AbortController();
      this.loading = false;
    },
    downloadDiamondResult() {
      // credit: https://www.bitdegree.org/learn/javascript-download
      let filename = "result.tsv";
      let element = document.createElement("a");
      element.setAttribute(
        "href",
        "data:application/json;charset=utf-8," +
          encodeURIComponent(this.downloadableDiamondResult)
      );
      element.setAttribute("download", filename);

      element.style.display = "none";
      document.body.appendChild(element);

      element.click();
      document.body.removeChild(element);
    },
    async onSequenceSearch(sequence: string) {
      this.downloadableDiamondResult = null;
      this.loading = true;
      this.$router.push({
        query: {
          ...this.$route.query,
          searchValue: sequence,
        },
      });
      const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sequence }),
        signal: this.controller.signal,
      };
      const url = new URL(`${this.diamondUrl}diamond`);
      const rawRes = await fetch(url.href, requestOptions);
      const res = await rawRes.json();
      if (!res["out"]) {
        // No significat hit was found in the DB.
        this.downloadableDiamondResult = "";
        this.loading = false;
        return;
      }
      // for each line in the output, split on tab and take the second element.
      const out = res["out"].trim().split("\n");
      const ids = out.map((line: string) => line.split("\t")[1]);
      const searchResult = await searchSpaces("word", ids);
      this.$emit("setMap", searchResult);
      const spaces = searchResult.spaces;
      let result =
        "query\tword\te_value\tidentical_amino_acids_percentage\tko\tlabel\tproduct\tgene_name\tsignificant\tpredicted_class\n";

      for (let i = 0; i < spaces.length; i++) {
        result +=
          out[i] +
          "\t" +
          (spaces[i].value.ko +
            "\t" +
            spaces[i].value.label +
            "\t" +
            spaces[i].value.product +
            "\t" +
            spaces[i].value.gene_name +
            "\t" +
            spaces[i].value.significant +
            "\t" +
            spaces[i].value.predicted_class);
      }

      this.downloadableDiamondResult = result;
      this.loading = false;
    },
  },
  watch: {
    loading(val) {
      this.$emit("setLoading", val);
    },
    sequenceFile(val) {
      if (!val) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.onSequenceSearch(e.target.result);
      };
      reader.readAsText(val[0]);
    },
  },
};
</script>
