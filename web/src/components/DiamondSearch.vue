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
  <v-container v-if="alertText" class="pa-0 pe-0 pb-0">
    <v-row>
      <v-col cols="11">
        <v-alert
          icon="mdi-alert-outline"
          color="error"
          density="compact"
          :text="alertText"
        ></v-alert>
      </v-col>
      <v-col cols="1"></v-col>
    </v-row>
  </v-container>
  <v-container v-else-if="downloadableDiamondResult" class="pa-0">
    <v-row v-for="(item, index) in diamondResults" dense>
      <v-divider v-if="index !== 0" class="ms-4 me-12" />
      <v-col cols="11">
        <v-list lines="one">
          <v-list-item subtitle="Query" :title="item.query"></v-list-item>
          <v-list-item subtitle="Word" :title="item.word"></v-list-item>
          <v-list-item subtitle="E-value" :title="item.eValue"></v-list-item>
          <v-list-item
            subtitle="Percent Identical"
            :title="item.identicalAminoAcidsPercentage"
          ></v-list-item>
        </v-list>
      </v-col>
      <v-col></v-col>
    </v-row>
    <v-row dense>
      <v-col cols="11">
        <v-btn @click="downloadDiamondResult" color="info">
          Download diamond results
        </v-btn>
      </v-col>
      <v-col cols="1"></v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { searchSpaces, Space } from "@/composables/spaces";
import { downloadTSVFile } from "@/composables/utils";

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
      alertText: "",
      controller: new AbortController(),
      diamondResults: null as Array<DiamondResult> | null,
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
      downloadTSVFile("sequence.tsv", this.downloadableDiamondResult);
    },
    async onSequenceSearch(sequence: string) {
      if (!sequence) {
        this.alertText = "Please enter a valid FASTA sequence.";
        return;
      }

      if (sequence[0] !== ">") {
        this.alertText =
          "Sequence must begin with an identifier that starts with '>'.";
        return;
      }

      this.downloadableDiamondResult = "";
      this.alertText = "";
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
        this.alertText = "No significat hit was found in the database.";
        this.loading = false;
        return;
      }
      // for each line in the output, split on tab and take the second element.
      const out = res["out"].trim().split("\n");
      this.diamondResults = new Array();
      for (const line of out) {
        const [query, word, eValue, identicalAminoAcidsPercentage] =
          line.split("\t");
        this.diamondResults.push({
          query,
          word,
          eValue,
          identicalAminoAcidsPercentage,
        });
      }

      const ids = out.map((line: string) => line.split("\t")[1]);
      const searchResult = await searchSpaces("word", ids);
      this.$emit("setMap", searchResult);
      const wordToSpace = new Map<string, Space>();
      for (const space of searchResult.spaces) {
        wordToSpace.set(space.value.word, space);
      }
      let result =
        "query\tword\te_value\tidentical_amino_acids_percentage\tko\tlabel\tproduct\tgene_name\tsignificant\tpredicted_class\n";

      for (const diamond of this.diamondResults) {
        result +=
          diamond.query +
          "\t" +
          diamond.word +
          "\t" +
          diamond.eValue +
          "\t" +
          diamond.identicalAminoAcidsPercentage;

        const space = wordToSpace.get(diamond.word);
        result +=
          "\t" +
          (space.value.ko +
            "\t" +
            space.value.label +
            "\t" +
            space.value.product +
            "\t" +
            space.value.gene_name +
            "\t" +
            space.value.significant +
            "\t" +
            space.value.predicted_class) +
          "\n";
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

interface DiamondResult {
  query: string;
  word: string;
  eValue: string;
  identicalAminoAcidsPercentage: string;
}
</script>
