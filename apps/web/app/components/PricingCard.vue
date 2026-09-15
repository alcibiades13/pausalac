<script setup lang="ts">
import { Card, Button } from '@pausalac/ui'
import type { PublicPlan } from '~/composables/usePublicPlans'

const props = defineProps<{ plan: PublicPlan; highlighted?: boolean }>()

const config = useRuntimeConfig()

const formattedPrice = computed(() =>
  new Intl.NumberFormat('sr-RS', { minimumFractionDigits: 0 }).format(Number(props.plan.price)),
)
</script>

<template>
  <Card :class="highlighted ? 'flex flex-col gap-4 ring-2 ring-primary' : 'flex flex-col gap-4'">
    <div>
      <p class="text-sm font-medium text-text-secondary">{{ plan.name }}</p>
      <p class="mt-1 text-2xl font-semibold text-navy">
        {{ formattedPrice }} {{ plan.currency }}
        <span class="text-sm font-normal text-text-secondary">/mes</span>
      </p>
    </div>
    <a :href="`${config.public.appUrl}/registracija`" class="mt-auto">
      <Button class="w-full" :variant="highlighted ? 'primary' : 'secondary'">Probaj besplatno</Button>
    </a>
  </Card>
</template>
