<script setup lang="ts">
import { Card, Button } from '@pausalac/ui'
import type { PublicPlan } from '~/composables/usePublicPlans'

const props = defineProps<{ plan: PublicPlan; highlighted?: boolean }>()

const config = useRuntimeConfig()
const { t } = useI18n()

// Always Serbian number-grouping convention for the RSD amount, regardless
// of UI language — the currency's home-locale format, not a translatable
// string (same reasoning as invoice/KPO PDFs always rendering Serbian).
const formattedPrice = computed(() =>
  new Intl.NumberFormat('sr-RS', { minimumFractionDigits: 0 }).format(Number(props.plan.price)),
)
</script>

<template>
  <Card
    :class="[
      'relative flex flex-col gap-5 transition-shadow',
      highlighted
        ? 'ring-2 ring-primary shadow-[0_10px_40px_-10px_rgba(10,10,10,0.25)] sm:-translate-y-2'
        : '',
    ]"
  >
    <span
      v-if="highlighted"
      class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-br from-primary to-primary-dark px-3 py-1 text-xs font-semibold text-white shadow-sm"
    >
      {{ t('pricingCard.mostPopular') }}
    </span>
    <div>
      <p class="text-sm font-medium text-text-secondary">{{ plan.name }}</p>
      <p class="mt-2 text-3xl font-semibold text-navy">
        {{ formattedPrice }} {{ plan.currency }}
        <span class="text-sm font-normal text-text-secondary">{{ t('pricingCard.perMonth') }}</span>
      </p>
    </div>
    <a :href="`${config.public.appUrl}/registracija`" target="_blank" rel="noopener noreferrer" class="mt-auto">
      <Button class="w-full" :variant="highlighted ? 'primary' : 'secondary'">{{ t('pricingCard.cta') }}</Button>
    </a>
  </Card>
</template>
