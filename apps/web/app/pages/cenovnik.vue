<script setup lang="ts">
import { Card } from '@pausalac/ui'
import PricingCard from '~/components/PricingCard.vue'
import Icon from '~/components/Icon.vue'
import Kicker from '~/components/Kicker.vue'

const { data: plans, pending, error } = usePublicPlans()
const { t, tm, rt } = useI18n()

useHead({
  title: t('meta.cenovnik.title'),
  meta: [{ name: 'description', content: t('meta.cenovnik.description') }],
})
</script>

<template>
  <div class="relative overflow-hidden">
    <div class="pointer-events-none absolute inset-0 -z-10" aria-hidden="true">
      <div class="absolute inset-0 bg-dot-grid opacity-60" />
    </div>

    <div class="mx-auto flex w-full max-w-6xl flex-col gap-20 px-4 py-16 sm:px-6 sm:py-24">
      <div v-reveal class="text-center">
        <Kicker :text="t('home.kickers.cenovnik')" class="justify-center" />
        <h1 class="mt-4 font-display text-3xl font-semibold text-navy sm:text-4xl">
          {{ t('cenovnik.heading') }}
        </h1>
        <p class="mx-auto mt-4 max-w-xl text-text-secondary">
          {{ t('cenovnik.subtitle') }}
        </p>
      </div>

      <p v-if="pending" class="text-center text-text-secondary">{{ t('cenovnik.loading') }}</p>
      <p v-else-if="error" class="text-center text-danger">
        {{ t('cenovnik.error') }}
      </p>
      <div v-else-if="plans && plans.length" class="grid grid-cols-1 gap-6 pt-3 sm:grid-cols-3">
        <div v-for="(plan, i) in plans" :key="plan.id" v-reveal :style="{ transitionDelay: `${i * 75}ms` }">
          <PricingCard :plan="plan" :highlighted="plan.identifier === 'professional'" />
        </div>
      </div>

      <div class="mx-auto w-full max-w-2xl">
        <h2 v-reveal class="mb-6 text-center font-display text-xl font-semibold text-navy">
          {{ t('cenovnik.faqHeading') }}
        </h2>
        <div class="flex flex-col gap-3">
          <Card
            v-for="(item, i) in tm('cenovnik.faq')"
            :key="i"
            v-reveal
            :style="{ transitionDelay: `${i * 75}ms` }"
            class="flex gap-3"
          >
            <span class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border bg-background text-navy">
              <Icon name="check-circle" :size="16" />
            </span>
            <div>
              <h3 class="font-medium text-navy">{{ rt(item.q) }}</h3>
              <p class="mt-1 text-sm text-text-secondary">{{ rt(item.a) }}</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  </div>
</template>
