<script setup lang="ts">
import { Card, Button } from '@pausalac/ui'
import AttentionMockup from '~/components/AttentionMockup.vue'
import PhoneMockup from '~/components/PhoneMockup.vue'
import PricingCard from '~/components/PricingCard.vue'
import Icon from '~/components/Icon.vue'
import Kicker from '~/components/Kicker.vue'

const config = useRuntimeConfig()
const { data: plans } = usePublicPlans()
const { t, tm, rt } = useI18n()
const localePath = useLocalePath()

useHead({
  title: t('meta.home.title'),
  meta: [{ name: 'description', content: t('meta.home.description') }],
})

// Icon names/step numbers aren't translatable content — kept as parallel,
// index-matched arrays here rather than duplicated across every locale
// file. `tm()` returns the raw {title, body} objects/arrays from
// i18n/locales/*.json, but — found the hard way, it rendered the
// compiled message AST as literal on-page text — each string LEAF still
// needs `rt()` to resolve to a plain string; `tm()` alone is only safe
// for the structural (array/object) shape.
const PROBLEM_ICONS = ['card', 'trending-up', 'check-circle', 'clock']
const MODULE_ICONS = ['module-invoices', 'module-clients', 'module-limits', 'module-kpo', 'module-obligations', 'module-documents']
const STEP_ICONS = ['module-clients', 'check-circle', 'arrow-right']
const STEP_NUMBERS = ['01', '02', '03']
</script>

<template>
  <div class="flex flex-col gap-24 pb-24 sm:gap-32">
    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div class="pointer-events-none absolute inset-0 -z-10 bg-dot-grid opacity-50" aria-hidden="true" />

      <div class="mx-auto grid w-full max-w-6xl grid-cols-1 items-center gap-14 px-4 pt-16 sm:px-6 sm:pt-20 lg:grid-cols-2 lg:gap-10">
        <div class="flex flex-col gap-6 text-center lg:text-left">
          <h1 class="font-display text-3xl font-extrabold leading-[1.1] tracking-tight sm:text-4xl lg:text-5xl">
            <span class="text-navy">{{ t('home.hero.titleMain') }}</span>{{ ' ' }}<span class="text-text-secondary">{{
              t('home.hero.titleAccent')
            }}</span>
          </h1>

          <p class="max-w-xl text-lg text-text-secondary lg:mx-0">
            {{ t('home.hero.subtitle') }}
          </p>

          <div class="flex flex-col gap-3 sm:flex-row sm:justify-center lg:justify-start">
            <a :href="`${config.public.appUrl}/registracija`" target="_blank" rel="noopener noreferrer">
              <Button class="w-full gap-2 sm:w-auto">
                {{ t('home.hero.ctaPrimary') }}
                <Icon name="arrow-right" :size="16" />
              </Button>
            </a>
            <a href="#kako-radi">
              <Button variant="secondary" class="w-full sm:w-auto">{{ t('home.hero.ctaSecondary') }}</Button>
            </a>
          </div>

          <p class="text-sm text-text-secondary">{{ t('home.hero.trust') }}</p>
        </div>

        <div v-reveal class="relative flex items-center justify-center gap-5 py-6 lg:justify-end lg:pr-4">
          <div class="w-[58%]">
            <AttentionMockup />
          </div>
          <div class="w-[38%] translate-y-12">
            <PhoneMockup />
          </div>
        </div>
      </div>
    </section>

    <!-- Problem -> rešenje -->
    <section id="kako-radi" class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <Kicker v-reveal :text="t('home.kickers.kakoRadi')" class="mb-6" />
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card
          v-for="(card, i) in tm('home.problem.cards')"
          :key="i"
          v-reveal
          :style="{ transitionDelay: `${i * 75}ms` }"
          class="flex flex-col gap-3 transition-shadow hover:shadow-[0_10px_40px_-10px_rgba(10,10,10,0.20)]"
        >
          <span class="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-background text-navy">
            <Icon :name="PROBLEM_ICONS[i]" :size="20" />
          </span>
          <h3 class="font-display text-base font-semibold text-navy">{{ rt(card.title) }}</h3>
          <p class="text-sm text-text-secondary">{{ rt(card.body) }}</p>
        </Card>
      </div>
    </section>

    <!-- Sve na jednom mestu -->
    <section class="bg-navy py-20 text-white">
      <div class="mx-auto w-full max-w-6xl px-4 sm:px-6">
        <Kicker v-reveal :text="t('home.kickers.moduli')" tone="inverted" class="mb-6" />
        <div v-reveal class="max-w-2xl">
          <h2 class="font-display text-2xl font-semibold sm:text-3xl">{{ t('home.modules.heading') }}</h2>
          <p class="mt-3 text-white/60">
            {{ t('home.modules.subtitle') }}
          </p>
        </div>

        <div class="mt-12 grid grid-cols-1 gap-x-10 sm:grid-cols-2">
          <div
            v-for="(item, i) in tm('home.modules.items')"
            :key="i"
            v-reveal
            :style="{ transitionDelay: `${i * 60}ms` }"
            class="flex items-start gap-4 border-t border-white/10 py-6 first:border-t-0 sm:[&:nth-child(2)]:border-t-0"
          >
            <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/15 text-white">
              <Icon :name="MODULE_ICONS[i]" :size="18" />
            </span>
            <div>
              <h3 class="font-display text-base font-semibold">{{ rt(item.title) }}</h3>
              <p class="mt-1 text-sm text-white/60">{{ rt(item.body) }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Attention Center deep-dive -->
    <section v-reveal class="mx-auto w-full max-w-3xl px-4 text-center sm:px-6">
      <Kicker :text="t('home.kickers.jedanStatus')" class="mb-4 justify-center" />
      <h2 class="font-display text-2xl font-semibold text-navy">{{ t('home.attention.heading') }}</h2>
      <p class="mt-4 text-text-secondary">
        {{ t('home.attention.body') }}
      </p>
    </section>

    <!-- Fakturisanje flow -->
    <section class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <Kicker v-reveal :text="t('home.kickers.fakturisanje')" class="mb-6 justify-center" />
      <h2 v-reveal class="mb-12 text-center font-display text-2xl font-semibold text-navy">
        {{ t('home.steps.heading') }}
      </h2>
      <div class="relative grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div
          class="pointer-events-none absolute inset-x-0 top-8 hidden border-t border-dashed border-border sm:block"
          aria-hidden="true"
        />
        <div
          v-for="(item, i) in tm('home.steps.items')"
          :key="i"
          v-reveal
          :style="{ transitionDelay: `${i * 100}ms` }"
          class="relative flex flex-col gap-3 rounded-2xl border border-border bg-surface p-6"
        >
          <div class="flex items-center justify-between">
            <span class="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-background text-navy">
              <Icon :name="STEP_ICONS[i]" :size="16" />
            </span>
            <span class="font-mono text-xs text-text-secondary">{{ STEP_NUMBERS[i] }}</span>
          </div>
          <h3 class="font-medium text-navy">{{ rt(item.title) }}</h3>
          <p class="text-sm text-text-secondary">{{ rt(item.body) }}</p>
        </div>
      </div>
    </section>

    <!-- Poređenje -->
    <section class="mx-auto w-full max-w-4xl px-4 sm:px-6">
      <Kicker v-reveal :text="t('home.kickers.poredjenje')" class="mb-6 justify-center" />
      <h2 v-reveal class="mb-8 text-center font-display text-2xl font-semibold text-navy">
        {{ t('home.comparison.heading') }}
      </h2>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div v-reveal class="rounded-2xl border border-border bg-surface p-6">
          <h3 class="mb-4 text-sm font-semibold text-text-secondary">{{ t('home.comparison.withoutTitle') }}</h3>
          <ul class="flex flex-col gap-3">
            <li
              v-for="(item, i) in tm('home.comparison.withoutItems')"
              :key="i"
              class="flex items-start gap-3 text-sm text-text-secondary"
            >
              <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-danger/10 text-danger">
                <Icon name="x-mark" :size="12" />
              </span>
              {{ rt(item) }}
            </li>
          </ul>
        </div>
        <div v-reveal class="rounded-2xl border-2 border-navy bg-surface p-6">
          <h3 class="mb-4 text-sm font-semibold text-navy">{{ t('home.comparison.withTitle') }}</h3>
          <ul class="flex flex-col gap-3">
            <li
              v-for="(item, i) in tm('home.comparison.withItems')"
              :key="i"
              class="flex items-start gap-3 text-sm text-navy"
            >
              <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-success/10 text-success">
                <Icon name="check" :size="12" />
              </span>
              {{ rt(item) }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Cenovnik preview -->
    <section class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <Kicker v-reveal :text="t('home.kickers.cenovnik')" class="mb-6 justify-center" />
      <h2 v-reveal class="mb-8 text-center font-display text-2xl font-semibold text-navy">
        {{ t('home.pricing.heading') }}
      </h2>
      <div v-if="plans && plans.length" class="grid grid-cols-1 gap-4 pt-3 sm:grid-cols-3">
        <div v-for="(plan, i) in plans" :key="plan.id" v-reveal :style="{ transitionDelay: `${i * 75}ms` }">
          <PricingCard :plan="plan" :highlighted="plan.identifier === 'professional'" />
        </div>
      </div>
      <div class="mt-6 text-center">
        <NuxtLink :to="localePath('/cenovnik')" class="text-sm font-medium text-navy hover:underline">
          {{ t('home.pricing.seeAll') }}
        </NuxtLink>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <div v-reveal class="grid grid-cols-1 overflow-hidden rounded-3xl sm:grid-cols-2">
        <div class="flex flex-col justify-center gap-6 bg-navy px-8 py-16 sm:px-12">
          <h2 class="font-display text-2xl font-semibold text-white sm:text-3xl">
            {{ t('home.finalCta.heading') }}
          </h2>
          <a :href="`${config.public.appUrl}/registracija`" target="_blank" rel="noopener noreferrer">
            <Button variant="secondary" class="w-fit gap-2 shadow-lg">
              {{ t('home.finalCta.cta') }}
              <Icon name="arrow-right" :size="16" />
            </Button>
          </a>
        </div>
        <div class="flex flex-col justify-center gap-3 bg-background px-8 py-16 sm:px-12">
          <div
            v-for="(fact, i) in tm('home.finalCta.facts')"
            :key="i"
            :style="{ marginLeft: `${i * 1.25}rem` }"
            class="w-fit rounded-xl border border-border bg-surface px-4 py-3 text-sm font-medium text-navy shadow-[0_10px_40px_-10px_rgba(10,10,10,0.15)]"
          >
            {{ rt(fact) }}
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
