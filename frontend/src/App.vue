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
  width: 100vw;
  min-height: 100vh;
  background-color: var(--color-background);
  overflow: hidden;
}

.main-content {
  flex: 1 1 auto;
  width: 0;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--color-background);
}

@media (max-width: 900px) {
  .app-container {
    flex-direction: column;
  }

  .main-content {
    width: 100%;
  }
}
</style>
