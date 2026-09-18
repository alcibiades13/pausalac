<script setup lang="ts">
// `align` also controls the leading dash: it's a visual anchor that
// only makes sense pointing into left-aligned text — a centered kicker
// has nothing for it to "lead into", so it's dropped entirely rather
// than centered alongside the text. `center-until-lg` (the one section
// that's centered on mobile and switches to left at `lg:`) hides the
// dash to match, then shows it once the text itself goes left.
withDefaults(
  defineProps<{ text: string; tone?: 'default' | 'inverted'; align?: 'left' | 'center' | 'center-until-lg' }>(),
  { align: 'left' },
)
</script>

<template>
  <span
    :class="[
      'flex items-center gap-2 font-mono text-xs font-medium uppercase tracking-wider',
      tone === 'inverted' ? 'text-white/60' : 'text-primary-dark',
      align === 'center' ? 'justify-center' : align === 'center-until-lg' ? 'justify-center lg:justify-start' : 'justify-start',
    ]"
  >
    <span
      v-if="align !== 'center'"
      :class="[
        'h-px w-4',
        tone === 'inverted' ? 'bg-white/30' : 'bg-primary-dark/40',
        align === 'center-until-lg' ? 'hidden lg:block' : '',
      ]"
      aria-hidden="true"
    />
    {{ text }}
  </span>
</template>
