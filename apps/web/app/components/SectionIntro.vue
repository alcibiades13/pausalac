<script setup lang="ts">
import Kicker from '~/components/Kicker.vue'

withDefaults(defineProps<{ kicker: string; heading: string; description?: string; tone?: 'default' | 'inverted' }>(), {
  tone: 'default',
})
</script>

<template>
  <div class="grid grid-cols-1 gap-6 md:grid-cols-5 md:items-end md:gap-12">
    <div class="md:col-span-2">
      <Kicker :text="kicker" :tone="tone" class="mb-4" />
      <h2 class="font-display text-2xl font-semibold sm:text-3xl" :class="tone === 'inverted' ? 'text-white' : 'text-navy'">
        {{ heading }}
      </h2>
    </div>
    <p v-if="description" class="md:col-span-3" :class="tone === 'inverted' ? 'text-white/60' : 'text-text-secondary'">
      {{ description }}
    </p>
  </div>
</template>
