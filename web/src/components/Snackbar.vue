<template>
  <v-snackbar v-model="show" multi-line>
    The original high-dimensional distances may look different in the
    two-dimensional representation.

    <template v-slot:actions>
      <v-btn color="info" variant="text" @click="onClose"> Close </v-btn>
    </template>
  </v-snackbar>
</template>

<script lang="ts">
export default {
  name: "Snackbar",
  emits: ["close"],
  props: {
    show: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    onClose() {
      this.$emit("close");
    },
  },
};
</script>
