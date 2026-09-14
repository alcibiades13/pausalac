<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div
    class="flex min-h-screen items-center justify-center bg-background px-4 py-12"
    style="background-image: radial-gradient(circle at 15% 10%, color-mix(in srgb, var(--color-primary) 10%, transparent), transparent 45%), radial-gradient(circle at 85% 90%, color-mix(in srgb, var(--color-primary-dark) 8%, transparent), transparent 45%)"
  >
    <div class="w-full max-w-sm">
      <h1 class="mb-6 text-center font-display text-xl font-semibold text-navy">{{ title }}</h1>
      <slot />
    </div>
  </div>
</template>
