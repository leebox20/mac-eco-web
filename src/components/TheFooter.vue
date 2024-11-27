<template>
  <footer class="bg-white py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center text-gray-500 text-sm">
        Copyright © 2011 — {{ currentYear }} China Macroeconomic Big Data AI Forecasting System. All rights reserved.
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref } from 'vue'

const currentYear = ref(new Date().getFullYear())
</script> 