<script setup lang="ts">
// @nuxtjs/i18n doesn't inject `<html lang>`/alternate-locale <link> tags
// automatically — useLocaleHead() computes them from the active route's
// locale, useHead() applies them. Without this, every locale renders
// with no `lang` attribute at all (real bug, caught by curling the built
// output rather than trusting the module's defaults).
useHead(useLocaleHead())
</script>

<template>
  <NuxtLayout>
    <NuxtRouteAnnouncer />
    <NuxtPage />
  </NuxtLayout>
</template>
