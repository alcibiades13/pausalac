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

const variantClasses: Record<string, string> = {
  primary: 'bg-primary',
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
