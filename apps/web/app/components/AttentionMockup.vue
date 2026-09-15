<script setup lang="ts">
import { Badge } from '@pausalac/ui'
import Icon from '~/components/Icon.vue'

/**
 * A real, hand-built recreation of the app's own Attention Center
 * (apps/app/src/components/AttentionItem.vue) — same icon+message+badge
 * row shape, same shared tokens/components, not a screenshot (no
 * browser tool in this environment to take one) or generic stock art.
 * Illustrative example content only — clearly a product demo, not a
 * claim about any real user's data. Framed as a small app window
 * (traffic-light dots + title bar) so it reads as "this is the real
 * product" rather than a loose card floating on the page.
 */
const { t } = useI18n()

const ITEM_ICONS = ['module-invoices', 'trending-up', 'module-obligations'] as const
const ITEM_TONES = ['danger', 'warning', 'warning'] as const
const ITEM_KEYS = ['item1', 'item2', 'item3'] as const

const items = ITEM_KEYS.map((key, i) => ({
  icon: ITEM_ICONS[i],
  tone: ITEM_TONES[i],
  message: t(`mockup.${key}`),
}))

const toneClasses: Record<string, string> = {
  danger: 'bg-danger/10 text-danger',
  warning: 'bg-warning/10 text-warning',
}
</script>

<template>
  <div class="w-full">
    <div class="overflow-hidden rounded-2xl border border-border bg-surface shadow-[0_10px_40px_-10px_rgba(10,10,10,0.20)]">
      <div class="flex items-center gap-1.5 border-b border-border bg-background px-4 py-2.5">
        <span class="h-2.5 w-2.5 rounded-full bg-danger/40" aria-hidden="true" />
        <span class="h-2.5 w-2.5 rounded-full bg-warning/40" aria-hidden="true" />
        <span class="h-2.5 w-2.5 rounded-full bg-success/40" aria-hidden="true" />
        <span class="ml-2 text-xs font-medium text-text-secondary">{{ t('mockup.windowLabel') }}</span>
      </div>

      <div class="p-5">
        <div class="mb-4 flex items-center justify-between gap-2">
          <h2 class="text-sm font-semibold text-navy">{{ t('mockup.attentionTitle') }}</h2>
          <span class="relative flex h-2.5 w-2.5 shrink-0" aria-hidden="true">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-danger/60" />
            <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-danger" />
          </span>
        </div>
        <div class="flex flex-col gap-2">
          <div
            v-for="item in items"
            :key="item.message"
            class="flex items-start gap-3 rounded-xl border border-border bg-white px-3.5 py-3"
          >
            <span :class="['flex h-8 w-8 shrink-0 items-center justify-center rounded-lg', toneClasses[item.tone]]">
              <Icon :name="item.icon" :size="16" />
            </span>
            <span class="flex-1 pt-1 text-sm leading-snug text-navy">{{ item.message }}</span>
            <Badge variant="warning" class="mt-0.5 shrink-0">{{ t('mockup.badge') }}</Badge>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
