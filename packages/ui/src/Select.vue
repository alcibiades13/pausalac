<script setup lang="ts">
import { useId } from 'vue'

const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    options: { value: string; label: string }[]
    error?: string
    hint?: string
    required?: boolean
    disabled?: boolean
  }>(),
  {
    required: false,
    disabled: false,
  },
)

const selectId = useId()
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" :for="selectId" class="text-sm font-medium text-navy">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <select
      :id="selectId"
      v-model="model"
      :required="required"
      :disabled="disabled"
      :aria-invalid="!!error"
      :aria-describedby="error ? `${selectId}-error` : hint ? `${selectId}-hint` : undefined"
      :class="[
        'rounded-lg border bg-surface px-3 py-2 text-sm text-navy',
        'transition-shadow focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40',
        'disabled:cursor-not-allowed disabled:bg-background disabled:opacity-60',
        error ? 'border-danger' : 'border-border',
      ]"
    >
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <p v-if="error" :id="`${selectId}-error`" class="text-sm text-danger">{{ error }}</p>
    <p v-else-if="hint" :id="`${selectId}-hint`" class="text-sm text-text-secondary">{{ hint }}</p>
  </div>
</template>
