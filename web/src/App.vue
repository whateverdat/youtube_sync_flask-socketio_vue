<script></script>

<template>
  <div class="flex-col">
    <Nav></Nav>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<style>
html.dark {
  color-scheme: dark;
}
</style>
