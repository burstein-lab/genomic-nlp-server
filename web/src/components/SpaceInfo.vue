<template>
  <v-list lines="one">
    <v-list-item
      v-for="[k, v] in spaceToInfo(space.value)"
      :key="k"
      :href="v?.toString()?.startsWith('https') ? v : undefined"
      :target="v?.toString()?.startsWith('https') ? '_blank' : undefined"
    >
      <v-list-item-content>
        <v-list-item-title>{{ displayedValue(k, v) }}</v-list-item-title>
        <v-list-item-subtitle
          :style="v?.toString()?.startsWith('https') ? 'color: #0077ee' : ''"
        >
          {{ k }}
        </v-list-item-subtitle>
      </v-list-item-content>

      <template v-if="isActionItem(k)" v-slot:append>
        <v-container class="text-center pa-0">
          <v-row justify="center" no-gutters>
            <v-col v-if="backable" class="pe-4">
              <v-tooltip
                text="Go to previously selected point"
                location="bottom"
              >
                <template v-slot:activator="{ props }">
                  <v-btn-group density="comfortable" v-bind="props">
                    <v-btn
                      color="info"
                      icon
                      density="comfortable"
                      @click="$emit('back')"
                    >
                      <v-icon>mdi-arrow-left</v-icon>
                    </v-btn>
                  </v-btn-group>
                </template>
              </v-tooltip>
            </v-col>
            <v-col class="pe-4">
              <v-tooltip text="Download sequence" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-btn-group density="comfortable" v-bind="props">
                    <v-btn
                      color="info"
                      icon
                      density="comfortable"
                      @click="$emit('downloadSequence')"
                    >
                      <v-icon>mdi-download</v-icon>
                    </v-btn>
                  </v-btn-group>
                </template>
              </v-tooltip>
            </v-col>
            <v-col class="pe-4">
              <v-tooltip text="Move to point" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-btn-group density="comfortable" v-bind="props">
                    <v-btn
                      color="info"
                      icon
                      density="comfortable"
                      @click="$emit('centerPoint')"
                    >
                      <v-icon>mdi-target</v-icon>
                    </v-btn>
                  </v-btn-group>
                </template>
              </v-tooltip>
            </v-col>
            <v-col>
              <v-tooltip text="Cancel selection" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-btn-group density="comfortable" v-bind="props">
                    <v-btn
                      color="grey"
                      icon
                      dark
                      @click="$emit('resetClickPoint')"
                    >
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-btn-group>
                </template>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-container>
      </template>
    </v-list-item>
  </v-list>
</template>

<script lang="ts">
import { truncate } from "@/composables/utils";
import { spaceToInfo, Space } from "@/composables/spaces";

export default {
  name: "SpaceInfo",
  components: {},
  props: {
    space: {
      type: Object as () => Space | null,
    },
    actionable: Boolean,
    backable: Boolean,
  },
  emits: ["centerPoint", "resetClickPoint", "downloadSequence", "back"],
  methods: {
    spaceToInfo(space: any) {
      return spaceToInfo(space);
    },
    displayedValue(k: string, v: string): string {
      const value = v === undefined || v === null ? "N/A" : v.toString();
      const length = this.isActionItem(k) ? 30 : 50;
      return truncate(value, length);
    },
    isActionItem(k: string): boolean {
      return this.actionable && k === "Word";
    },
  },
};
</script>
