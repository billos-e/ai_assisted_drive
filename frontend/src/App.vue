<template>
  <div class="app-container">
    <div class="bg-mesh"></div>
    <Sidebar 
      :activeSection="activeSection"
      @navigate="handleNavigation"
    />
    <main class="main-content">
      <Transition name="page" mode="out-in">
        <Repository v-if="activeSection === 'repository'" :key="'repo'" />
        <Chat v-else-if="activeSection === 'chat'" :key="'chat'" />
        <Settings v-else-if="activeSection === 'settings'" :key="'settings'" />
      </Transition>
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
  height: 100vh;
  background-color: var(--color-background);
  overflow: hidden;
  position: relative;
}

.bg-mesh {
  position: absolute;
  inset: 0;
  z-index: 0;
  opacity: 0.4;
  background: 
    radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
  filter: blur(80px);
  pointer-events: none;
}

.main-content {
  flex: 1;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Page Transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
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
