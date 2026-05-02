<template>
  <div class="app-container">
    <Sidebar 
      :activeSection="activeSection"
      @navigate="handleNavigation"
    />
    <main class="main-content">
      <Repository v-if="activeSection === 'repository'" />
      <Chat v-else-if="activeSection === 'chat'" />
      <Settings v-else-if="activeSection === 'settings'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Repository from './pages/Repository.vue'
import Chat from './pages/Chat.vue'
import Settings from './pages/Settings.vue'

const activeSection = ref('repository')

const handleNavigation = (section) => {
  activeSection.value = section
}
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background-color: var(--color-background);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--color-background);
}
</style>
