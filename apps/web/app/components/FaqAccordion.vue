<script setup lang="ts">
import { ref } from 'vue'
import Icon from '~/components/Icon.vue'

defineProps<{ items: { q: string; a: string }[] }>()

const openIndex = ref<number | null>(0)

function toggle(i: number) {
  openIndex.value = openIndex.value === i ? null : i
}
</script>

<template>
  <div class="flex flex-col divide-y divide-border rounded-2xl border border-border bg-surface">
    <div v-for="(item, i) in items" :key="i">
      <h3>
        <button
          type="button"
          class="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
          :aria-expanded="openIndex === i"
          :aria-controls="`faq-panel-${i}`"
          @click="toggle(i)"
        >
          <span class="font-medium text-navy">{{ item.q }}</span>
          <Icon
            name="chevron-down"
            :size="18"
            class="shrink-0 text-text-secondary transition-transform"
            :class="openIndex === i ? 'rotate-180' : ''"
          />
        </button>
      </h3>
      <div v-if="openIndex === i" :id="`faq-panel-${i}`" class="px-5 pb-4 text-sm text-text-secondary">
        {{ item.a }}
      </div>
    </div>
  </div>
</template>
