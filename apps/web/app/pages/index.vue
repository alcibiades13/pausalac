<script setup lang="ts">
import { computed, ref } from 'vue'
import { Card, Button } from '@pausalac/ui'
import PricingCard from '~/components/PricingCard.vue'
import Icon from '~/components/Icon.vue'
import Kicker from '~/components/Kicker.vue'
import ScreenshotFrame from '~/components/ScreenshotFrame.vue'
import FaqAccordion from '~/components/FaqAccordion.vue'

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
const SPOTLIGHT_SCREENSHOTS = ['/screenshots/fakture.png', '/screenshots/kpo.png', '/screenshots/limiti.png']
const SUPPORTING_ICONS = ['module-clients', 'module-obligations', 'module-documents']
const STEP_SCREENSHOTS = ['/screenshots/korak-klijent.png', '/screenshots/korak-stavke.png', '/screenshots/korak-pregled.png']
const STEP_NUMBERS = ['01', '02', '03']

const faqItems = computed(() =>
  (tm('home.faq.items') as { q: any; a: any }[]).map((item) => ({ q: rt(item.q), a: rt(item.a) })),
)

// "Sve na jednom mestu" tabs — one active module at a time (real
// screenshot + its own description large enough to actually read,
// rather than three small alternating blocks) instead of a static
// alternating-image list.
const activeModuleTab = ref(0)
const moduleSpotlight = computed(() =>
  (tm('home.modules.spotlight') as { title: any; body: any; screenshotAlt: any }[]).map((item) => ({
    title: rt(item.title),
    body: rt(item.body),
    screenshotAlt: rt(item.screenshotAlt),
  })),
)
</script>

<template>
  <div class="flex flex-col gap-24 pb-24 sm:gap-32">
    <!-- Hero -->
    <section class="relative z-0 overflow-hidden">
      <div class="pointer-events-none absolute inset-0 -z-20 bg-gradient-to-br from-surface to-background" aria-hidden="true" />
      <div
        class="pointer-events-none absolute inset-y-0 right-0 -z-20 hidden w-1/2 bg-[radial-gradient(circle_at_100%_100%,_var(--color-primary),_transparent_60%)] opacity-20 lg:block"
        aria-hidden="true"
      />
      <div class="pointer-events-none absolute inset-0 -z-10 bg-dot-grid opacity-50" aria-hidden="true" />

      <div class="grid w-full grid-cols-1 items-center gap-14 px-4 py-16 sm:px-6 sm:py-24 lg:grid-cols-2 lg:gap-10 xl:px-12">
        <div class="flex flex-col items-center gap-6 text-center lg:mx-auto lg:w-fit lg:items-start lg:text-left">
          <h1 class="font-display text-6xl font-black leading-[1.05] tracking-tight sm:text-7xl 2xl:text-8xl">
            <span class="text-navy">{{ t('home.hero.titleMain') }}</span><br />
            <span class="text-text-secondary">{{ t('home.hero.titleAccent') }}</span>
          </h1>

          <ul class="flex flex-col gap-3 text-left">
            <li
              v-for="(fact, i) in tm('home.hero.facts')"
              :key="i"
              class="flex items-start gap-3 text-lg text-text-secondary"
            >
              <span class="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/15 text-primary-dark">
                <Icon name="check" :size="12" />
              </span>
              {{ rt(fact) }}
            </li>
          </ul>

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

        <div v-reveal class="relative flex items-center justify-center py-6 lg:justify-end">
          <div class="w-[82%]">
            <ScreenshotFrame src="/screenshots/hero-laptop.png" :alt="t('home.hero.laptopScreenshotAlt')" />
          </div>
          <div class="w-[24%] -ml-10 translate-y-16">
            <ScreenshotFrame
              src="/screenshots/hero-mobile.png"
              :alt="t('home.hero.mobileScreenshotAlt')"
              shadow-class="shadow-[0_28px_70px_-16px_rgba(10,10,10,0.35)]"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Attention Center deep-dive — moved right after the hero: this is
         the signature feature (master prompt's Attention Center), so it
         gets the biggest visual treatment on the page instead of three
         sentences halfway down. -->
    <section v-reveal class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <div class="grid grid-cols-1 items-center gap-10 lg:grid-cols-2 lg:gap-16">
        <div class="text-center lg:text-left">
          <Kicker :text="t('home.kickers.jedanStatus')" class="mb-4 justify-center lg:justify-start" />
          <h2 class="font-display text-2xl font-semibold text-navy sm:text-3xl">{{ t('home.attention.heading') }}</h2>
          <p class="mt-4 text-text-secondary">
            {{ t('home.attention.body') }}
          </p>
          <ul class="mt-6 flex flex-col gap-3 text-left">
            <li
              v-for="(note, i) in tm('home.attention.annotations')"
              :key="i"
              class="flex items-start gap-3 text-sm text-navy"
            >
              <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary-dark">
                <Icon name="arrow-right" :size="12" />
              </span>
              {{ rt(note) }}
            </li>
          </ul>
        </div>
        <ScreenshotFrame src="/screenshots/attention-center.png" :alt="t('home.attention.screenshotAlt')" />
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

    <!-- Sve na jednom mestu — a tabbed switcher over the 3 modules with
         real screenshots (one big screenshot + a properly-sized
         description at a time, not three small alternating blocks),
         plus the remaining 3 modules as a smaller supporting icon+text
         row underneath. -->
    <section class="bg-navy py-20 text-white">
      <div class="mx-auto w-full max-w-6xl px-4 sm:px-6">
        <Kicker v-reveal :text="t('home.kickers.moduli')" tone="inverted" class="mb-6" />
        <div v-reveal class="max-w-2xl">
          <h2 class="font-display text-2xl font-semibold sm:text-3xl">{{ t('home.modules.heading') }}</h2>
          <p class="mt-3 text-white/60">
            {{ t('home.modules.subtitle') }}
          </p>
        </div>

        <div v-reveal class="mt-14 lg:grid lg:grid-cols-[240px_1fr] lg:items-start lg:gap-14">
          <div class="mb-8 flex gap-2 overflow-x-auto pb-1 lg:mb-0 lg:flex-col lg:gap-1 lg:overflow-visible lg:pb-0">
            <button
              v-for="(item, i) in moduleSpotlight"
              :key="i"
              type="button"
              class="shrink-0 rounded-lg px-4 py-3 text-left font-display text-sm font-semibold transition-colors lg:shrink"
              :class="activeModuleTab === i ? 'bg-white/10 text-white' : 'text-white/50 hover:bg-white/5 hover:text-white/80'"
              @click="activeModuleTab = i"
            >
              {{ item.title }}
            </button>
          </div>

          <Transition name="fade-slide" mode="out-in">
            <div :key="activeModuleTab">
              <p class="mb-6 max-w-xl text-lg text-white/70">{{ moduleSpotlight[activeModuleTab]?.body }}</p>
              <ScreenshotFrame
                :src="SPOTLIGHT_SCREENSHOTS[activeModuleTab]"
                :alt="moduleSpotlight[activeModuleTab]?.screenshotAlt ?? ''"
              />
            </div>
          </Transition>
        </div>

        <div class="mt-16 grid grid-cols-1 gap-x-10 border-t border-white/10 pt-10 sm:grid-cols-3">
          <div
            v-for="(item, i) in tm('home.modules.supporting')"
            :key="i"
            v-reveal
            :style="{ transitionDelay: `${i * 60}ms` }"
            class="flex items-start gap-4 py-4"
          >
            <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/15 text-white">
              <Icon :name="SUPPORTING_ICONS[i]" :size="18" />
            </span>
            <div>
              <h3 class="font-display text-base font-semibold">{{ rt(item.title) }}</h3>
              <p class="mt-1 text-sm text-white/60">{{ rt(item.body) }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Fakturisanje flow — mini real screenshots of each step instead of
         abstract icon cards, proving the "tri koraka" claim rather than
         just stating it. Numbered badges + a connecting timeline line
         (sm+) make the "three steps in sequence" claim visually obvious
         instead of just three cards that happen to sit in a row. -->
    <section class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <Kicker v-reveal :text="t('home.kickers.fakturisanje')" class="mb-6 justify-center" />
      <h2 v-reveal class="mb-16 text-center font-display text-2xl font-semibold text-navy">
        {{ t('home.steps.heading') }}
      </h2>
      <div class="relative grid grid-cols-1 gap-12 sm:grid-cols-3 sm:gap-8">
        <div
          class="pointer-events-none absolute inset-x-0 top-6 hidden h-px bg-gradient-to-r from-transparent via-border to-transparent sm:block"
          aria-hidden="true"
        />
        <div
          v-for="(item, i) in tm('home.steps.items')"
          :key="i"
          v-reveal
          :style="{ transitionDelay: `${i * 120}ms` }"
          class="relative flex flex-col items-center gap-4 text-center"
        >
          <span
            class="relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-dark font-display text-lg font-bold text-white shadow-[0_10px_30px_-8px_rgba(170,118,255,0.55)]"
          >
            {{ STEP_NUMBERS[i] }}
          </span>
          <ScreenshotFrame
            class="w-full transition-transform duration-300 hover:-translate-y-1"
            :src="STEP_SCREENSHOTS[i]"
            :alt="rt(item.screenshotAlt)"
          />
          <h3 class="font-medium text-navy">{{ rt(item.title) }}</h3>
          <p class="text-sm text-text-secondary">{{ rt(item.body) }}</p>
        </div>
      </div>
    </section>

    <!-- Poređenje -->
    <section class="border-y border-border bg-surface py-20">
      <div class="mx-auto w-full max-w-4xl px-4 sm:px-6">
        <Kicker v-reveal :text="t('home.kickers.poredjenje')" class="mb-6 justify-center" />
        <h2 v-reveal class="mb-8 text-center font-display text-2xl font-semibold text-navy">
          {{ t('home.comparison.heading') }}
        </h2>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div v-reveal class="rounded-2xl border border-border bg-background p-6">
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
          <div v-reveal class="rounded-2xl border-2 border-navy bg-background p-6">
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

    <!-- FAQ — a real accordion (functional layout variation, not another
         static card grid), and reduces friction right before the pricing
         preview above and the final CTA below. -->
    <section class="mx-auto w-full max-w-3xl px-4 sm:px-6">
      <Kicker v-reveal :text="t('home.kickers.faq')" class="mb-6 justify-center" />
      <h2 v-reveal class="mb-8 text-center font-display text-2xl font-semibold text-navy">
        {{ t('home.faq.heading') }}
      </h2>
      <FaqAccordion v-reveal :items="faqItems" />
    </section>

    <!-- Baza znanja teaser -->
    <section class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <Kicker v-reveal :text="t('home.knowledgeBase.kicker')" class="mb-6 justify-center" />
      <h2 v-reveal class="mb-3 text-center font-display text-2xl font-semibold text-navy">
        {{ t('home.knowledgeBase.heading') }}
      </h2>
      <p v-reveal class="mx-auto mb-10 max-w-xl text-center text-text-secondary">
        {{ t('home.knowledgeBase.subtitle') }}
      </p>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <NuxtLink
          v-for="(article, i) in tm('articles.list')"
          :key="i"
          v-reveal
          :style="{ transitionDelay: `${i * 75}ms` }"
          :to="localePath(`/baza-znanja/${rt(article.slug)}`)"
        >
          <Card class="flex h-full flex-col gap-2 transition-shadow hover:shadow-[0_10px_40px_-10px_rgba(10,10,10,0.20)]">
            <span class="font-mono text-xs text-text-secondary">{{ rt(article.readTime) }}</span>
            <h3 class="font-display text-base font-semibold text-navy">{{ rt(article.title) }}</h3>
            <p class="text-sm text-text-secondary">{{ rt(article.excerpt) }}</p>
            <span class="mt-auto pt-2 text-sm font-medium text-primary-dark">{{ t('home.knowledgeBase.readMore') }}</span>
          </Card>
        </NuxtLink>
      </div>
      <div class="mt-6 text-center">
        <NuxtLink :to="localePath('/baza-znanja')" class="text-sm font-medium text-navy hover:underline">
          {{ t('home.knowledgeBase.seeAll') }}
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

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
