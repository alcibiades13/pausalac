<script setup lang="ts">
import { Card, Badge } from '@pausalac/ui'

/**
 * A real, hand-built recreation of the app's own Attention Center
 * (apps/app/src/components/AttentionItem.vue) — same icon+message+badge
 * row shape, same shared tokens/components, not a screenshot (no
 * browser tool in this environment to take one) or generic stock art.
 * Illustrative example content only — clearly a product demo, not a
 * claim about any real user's data.
 */
const items = [
  { icon: '🔴', message: 'Faktura #2026-014 kasni 6 dana', badge: 'Pogledaj' },
  { icon: '📈', message: 'Ostalo ti je 18% do godišnjeg limita', badge: 'Pogledaj' },
  { icon: '🧾', message: 'Poreska obaveza dospeva za 4 dana', badge: 'Pogledaj' },
]
</script>

<template>
  <Card class="w-full max-w-md">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-sm font-semibold text-navy">3 stvari zahtevaju tvoju pažnju</h2>
      <span class="h-2 w-2 rounded-full bg-danger" aria-hidden="true" />
    </div>
    <div class="flex flex-col gap-2">
      <div
        v-for="item in items"
        :key="item.message"
        class="flex items-center gap-3 rounded-lg border border-border bg-white px-4 py-3"
      >
        <span aria-hidden="true">{{ item.icon }}</span>
        <span class="flex-1 text-sm text-navy">{{ item.message }}</span>
        <Badge variant="warning">{{ item.badge }}</Badge>
      </div>
    </div>
  </Card>
</template>
