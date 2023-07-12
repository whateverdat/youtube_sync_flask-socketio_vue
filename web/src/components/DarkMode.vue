<script setup>
import { useDark, useToggle } from '@vueuse/core'

const isDark = useDark();
const toggleDark = useToggle(isDark);
</script>
<template>
  <div>
    <button class="button" @click="toggleDark()">
      Turn {{ isDark ? 'on' : 'off'  }} the Lights
    </button>
  </div>
</template>
