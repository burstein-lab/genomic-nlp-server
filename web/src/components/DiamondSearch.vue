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
    append-icon="mdi-send"
    @click:append="onSequenceSearch(sequence)"
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
  <v-btn v-if="downloadableDiamondResult" @click="downloadDiamondResult">
    Download diamond result
  </v-btn>
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
      downloadableDiamondResult: "",
    };
  },
  emits: ["setMap", "setLoading"],
  methods: {
    downloadDiamondResult() {
      // credit: https://www.bitdegree.org/learn/javascript-download
      let filename = "file.tsv";
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
      this.$emit("setLoading", true);
      const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sequence }),
      };
      const url = new URL(`${this.diamondUrl}diamond`);
      const rawRes = await fetch(url.href, requestOptions);
      const res = await rawRes.json();
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
      this.$emit("setLoading", false);
    },
  },
  watch: {
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
