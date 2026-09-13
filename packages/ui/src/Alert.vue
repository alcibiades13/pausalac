<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'success' | 'warning' | 'danger' | 'info'
  }>(),
  {
    variant: 'info',
  },
)

const variantClasses: Record<string, string> = {
  success: 'bg-success/10 text-success border-success/30',
  warning: 'bg-warning/10 text-warning border-warning/30',
  danger: 'bg-danger/10 text-danger border-danger/30',
  info: 'bg-primary/10 text-primary border-primary/30',
}
</script>

<template>
  <div role="alert" :class="['rounded-lg border px-4 py-3 text-sm', variantClasses[variant]]">
    <slot />
  </div>
</template>
