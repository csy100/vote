<script setup lang="ts">
import PollComponent from './components/PollComponent.vue'
</script>

<template>
  <div class="app">
    <header>
      <h1>在线投票系统</h1>
    </header>
    <main>
      <PollComponent />
    </main>
  </div>
</template>

<style>
.app {
  font-family: Arial, sans-serif;
  min-height: 100vh;
  background-color: #f5f7fa;
}

header {
  background-color: #409EFF;
  color: white;
  padding: 20px;
  text-align: center;
}

header h1 {
  margin: 0;
  font-size: 28px;
}

main {
  padding: 20px;
}
</style>
