<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    value: number
    max?: number
    variant?: 'primary' | 'success' | 'warning' | 'danger'
    label?: string
  }>(),
  {
    max: 100,
    variant: 'primary',
  },
)

// 'primary' deliberately renders `bg-primary-dark`, not `bg-primary`:
// --color-primary is a pale, user-specified violet (packages/config/
// tokens.css — a deliberate, contrast-disclosed exception to this
// project's usual AA rule) that would read as a weak, barely-visible
// thin fill; primary-dark is the same hue family but genuinely passes
// AA and actually shows up as a slider/progress bar.
const variantClasses: Record<string, string> = {
  primary: 'bg-primary-dark',
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
}

const percentage = computed(() => Math.min(100, Math.max(0, (props.value / props.max) * 100)))
</script>

<template>
  <div
    role="progressbar"
    :aria-valuenow="value"
    :aria-valuemin="0"
    :aria-valuemax="max"
    :aria-label="label"
    class="h-2 w-full overflow-hidden rounded-full bg-background"
  >
    <div
      class="h-full rounded-full transition-all"
      :class="variantClasses[variant]"
      :style="{ width: `${percentage}%` }"
    />
  </div>
</template>
