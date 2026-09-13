<script setup lang="ts">
import { useId } from 'vue'

const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    type?: string
    placeholder?: string
    error?: string
    hint?: string
    required?: boolean
    disabled?: boolean
    autocomplete?: string
  }>(),
  {
    type: 'text',
    required: false,
    disabled: false,
  },
)

const inputId = useId()
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" :for="inputId" class="text-sm font-medium text-navy">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <input
      :id="inputId"
      v-model="model"
      :type="type"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :autocomplete="autocomplete"
      :aria-invalid="!!error"
      :aria-describedby="error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined"
      :class="[
        'rounded-lg border bg-white px-3 py-2 text-sm text-navy placeholder:text-text-secondary',
        'focus:outline-none focus:ring-2 focus:ring-primary/40',
        'disabled:cursor-not-allowed disabled:bg-background disabled:opacity-60',
        error ? 'border-danger' : 'border-border',
      ]"
    />
    <p v-if="error" :id="`${inputId}-error`" class="text-sm text-danger">{{ error }}</p>
    <p v-else-if="hint" :id="`${inputId}-hint`" class="text-sm text-text-secondary">{{ hint }}</p>
  </div>
</template>
