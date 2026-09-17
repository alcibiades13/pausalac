<script setup lang="ts">
import { Card } from '@pausalac/ui'
import Kicker from '~/components/Kicker.vue'

const { t, tm, rt } = useI18n()
const localePath = useLocalePath()

useHead({
  title: t('articles.meta.title'),
  meta: [{ name: 'description', content: t('articles.meta.description') }],
})
</script>

<template>
  <div class="mx-auto flex w-full max-w-4xl flex-col gap-10 px-4 py-16 sm:px-6 sm:py-24">
    <div v-reveal class="text-center">
      <Kicker :text="t('home.knowledgeBase.kicker')" class="justify-center" />
      <h1 class="mt-4 font-display text-3xl font-semibold text-navy sm:text-4xl">
        {{ t('home.knowledgeBase.heading') }}
      </h1>
      <p class="mx-auto mt-4 max-w-xl text-text-secondary">
        {{ t('home.knowledgeBase.subtitle') }}
      </p>
    </div>

    <div class="flex flex-col gap-4">
      <NuxtLink
        v-for="(article, i) in tm('articles.list')"
        :key="i"
        v-reveal
        :style="{ transitionDelay: `${i * 75}ms` }"
        :to="localePath(`/baza-znanja/${rt(article.slug)}`)"
      >
        <Card class="flex flex-col gap-2 transition-shadow hover:shadow-[0_10px_40px_-10px_rgba(10,10,10,0.20)]">
          <span class="font-mono text-xs text-text-secondary">{{ rt(article.readTime) }}</span>
          <h2 class="font-display text-lg font-semibold text-navy">{{ rt(article.title) }}</h2>
          <p class="text-sm text-text-secondary">{{ rt(article.excerpt) }}</p>
          <span class="text-sm font-medium text-primary-dark">{{ t('home.knowledgeBase.readMore') }}</span>
        </Card>
      </NuxtLink>
    </div>
  </div>
</template>
