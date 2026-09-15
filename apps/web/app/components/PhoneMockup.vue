<script setup lang="ts">
import Icon from '~/components/Icon.vue'

/**
 * The hero's second, "mobile" mockup — paired with AttentionMockup (the
 * "desktop" one) in a side-by-side composition, replacing the earlier
 * single-floating-card hero (reference: privy.io's phone-overlapping-
 * dashboard hero). Shows the app's real mobile bottom nav
 * (apps/app/src/components/MobileBottomNav.vue — same four icons, same
 * order: Početna/Fakture/Limiti/Dokumenti) inside a phone frame, not
 * invented mobile UI, so it stays honest about what the product's mobile
 * view actually looks like.
 */
const { t } = useI18n()

const NAV_ICONS = ['module-invoices', 'trending-up', 'module-documents'] as const
const NAV_KEYS = ['fakture', 'limiti', 'dokumenti'] as const
</script>

<template>
  <div class="w-full max-w-[220px] overflow-hidden rounded-[2rem] border-4 border-navy bg-surface shadow-[0_10px_40px_-10px_rgba(10,10,10,0.35)]">
    <div class="flex items-center justify-center bg-navy py-1.5">
      <span class="h-1 w-10 rounded-full bg-white/30" aria-hidden="true" />
    </div>

    <div class="flex flex-col gap-3 p-3.5">
      <p class="text-[10px] font-medium uppercase tracking-wide text-text-secondary">{{ t('mockup.phoneLabel') }}</p>
      <p class="font-display text-xl font-semibold text-navy">248.500 RSD</p>

      <div class="flex items-center gap-2 rounded-xl border border-border bg-background px-2.5 py-2">
        <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-success/10 text-success">
          <Icon name="check" :size="12" />
        </span>
        <span class="text-[11px] leading-tight text-navy">{{ t('mockup.phoneToast') }}</span>
      </div>
    </div>

    <div class="flex items-center justify-around border-t border-border px-2 py-2.5">
      <span
        v-for="(icon, i) in NAV_ICONS"
        :key="NAV_KEYS[i]"
        class="flex flex-col items-center gap-0.5 text-text-secondary"
      >
        <Icon :name="icon" :size="16" />
        <span class="text-[9px]">{{ t(`mockup.phoneNav.${NAV_KEYS[i]}`) }}</span>
      </span>
    </div>
  </div>
</template>
