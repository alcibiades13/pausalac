<script setup lang="ts">
const route = useRoute()
const { t, tm, rt } = useI18n()
const localePath = useLocalePath()

const slug = route.params.slug as string

// tm() resolves every string leaf to a compiled-message resource (found
// the hard way in index.vue — see its own comment), so these come back
// loosely typed; `any` here matches how the rest of this codebase treats
// tm()/rt() output rather than fighting vue-i18n's generic inference.
const listEntry = (tm('articles.list') as { slug: any; title: any; readTime: any }[]).find(
  (item) => rt(item.slug) === slug,
)
const content = (tm('articles.content') as Record<string, { dek: any; sections: { heading: any; paragraphs: any[] }[] }>)[slug]

if (!listEntry || !content) {
  throw createError({ statusCode: 404, statusMessage: 'Not Found' })
}

const title = rt(listEntry.title)
const dek = rt(content.dek)
const sections = content.sections.map((section) => ({
  heading: rt(section.heading),
  paragraphs: section.paragraphs.map((p) => rt(p)),
}))

useHead({
  title,
  meta: [{ name: 'description', content: dek }],
})
</script>

<template>
  <article class="mx-auto flex w-full max-w-2xl flex-col gap-8 px-4 py-16 sm:px-6 sm:py-24">
    <div v-reveal>
      <NuxtLink :to="localePath('/baza-znanja')" class="text-sm font-medium text-text-secondary hover:text-primary-dark">
        {{ t('articles.backToList') }}
      </NuxtLink>
      <h1 class="mt-4 font-display text-3xl font-semibold text-navy sm:text-4xl">{{ title }}</h1>
      <p class="mt-3 text-lg text-text-secondary">{{ dek }}</p>
    </div>

    <div v-for="(section, i) in sections" :key="i" v-reveal class="flex flex-col gap-3">
      <h2 class="font-display text-xl font-semibold text-navy">{{ section.heading }}</h2>
      <p v-for="(paragraph, j) in section.paragraphs" :key="j" class="text-text-secondary">
        {{ paragraph }}
      </p>
    </div>
  </article>
</template>
