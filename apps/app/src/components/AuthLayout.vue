<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background px-4 py-12">
    <div class="w-full max-w-sm">
      <h1 class="mb-6 text-center text-xl font-semibold text-navy">{{ title }}</h1>
      <slot />
    </div>
  </div>
</template>
