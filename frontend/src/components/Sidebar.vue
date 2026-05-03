<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <div class="logo" @click="$emit('toggle-collapse')" title="Toggle Sidebar">
        <Sparkles :size="24" class="logo-icon-svg" />
        <span v-if="!isCollapsed" class="logo-text">AI Drive</span>
      </div>
    </div>

    <div class="sidebar-content">
      <div class="menu-section">
        <h3 v-if="!isCollapsed" class="section-title">MENU</h3>
        <nav class="sidebar-nav">
          <button
            class="nav-item"
            :class="{ active: activeSection === 'repository' }"
            @click="$emit('navigate', 'repository')"
            :title="isCollapsed ? 'All files' : ''"
          >
            <Folder :size="20" class="nav-icon" />
            <span v-if="!isCollapsed" class="nav-label">All files</span>
          </button>

          <button
            class="nav-item"
            :class="{ active: activeSection === 'recent' }"
            @click="$emit('navigate', 'recent')"
            :title="isCollapsed ? 'Recent' : ''"
          >
            <Clock :size="20" class="nav-icon" />
            <span v-if="!isCollapsed" class="nav-label">Recent</span>
          </button>

          <button
            class="nav-item"
            :class="{ active: activeSection === 'starred' }"
            @click="$emit('navigate', 'starred')"
            :title="isCollapsed ? 'Starred' : ''"
          >
            <Star :size="20" class="nav-icon" />
            <span v-if="!isCollapsed" class="nav-label">Starred</span>
          </button>

          <button
            class="nav-item"
            :class="{ active: activeSection === 'trash' }"
            @click="$emit('navigate', 'trash')"
            :title="isCollapsed ? 'Trash' : ''"
          >
            <Trash2 :size="20" class="nav-icon" />
            <span v-if="!isCollapsed" class="nav-label">Trash</span>
          </button>
        </nav>
      </div>

      <div class="menu-section">
        <h3 v-if="!isCollapsed" class="section-title">SYSTEM</h3>
        <nav class="sidebar-nav">
          <button
            class="nav-item"
            :class="{ active: activeSection === 'chat' }"
            @click="$emit('navigate', 'chat')"
            :title="isCollapsed ? 'AI Chat' : ''"
          >
            <MessageSquare :size="20" class="nav-icon" />
            <span v-if="!isCollapsed" class="nav-label">AI Chat</span>
          </button>

          <button
            class="nav-item"
            :class="{ active: activeSection === 'settings' }"
            @click="$emit('navigate', 'settings')"
            :title="isCollapsed ? 'Settings' : ''"
          >
            <Settings2 :size="20" class="nav-icon" />
            <span v-if="!isCollapsed" class="nav-label">Settings</span>
          </button>
        </nav>
      </div>
    </div>

    <div class="sidebar-footer">
      <div v-if="!isCollapsed" class="storage-status">
        <div class="storage-info">
          <span class="storage-label">Storage</span>
          <span class="storage-value">75% used</span>
        </div>
        <div class="storage-bar">
          <div class="storage-fill" style="width: 75%"></div>
        </div>
        <p class="storage-details">6.4 GB of 10 GB used</p>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { 
  Folder, 
  MessageSquare, 
  Settings2, 
  Sparkles, 
  Clock, 
  Star, 
  Trash2
} from 'lucide-vue-next'

defineProps({
  activeSection: {
    type: String,
    default: 'repository'
  },
  isCollapsed: {
    type: Boolean,
    default: false
  }
})

defineEmits(['navigate', 'create-new', 'toggle-collapse'])
</script>

<style scoped>
.sidebar {
  width: 260px;
  flex: 0 0 260px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface);
  position: relative;
  z-index: 20;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.sidebar.collapsed {
  width: 80px;
  flex: 0 0 80px;
}

.sidebar-header {
  padding: var(--spacing-xl) var(--spacing-lg);
}

.sidebar.collapsed .sidebar-header {
  padding: var(--spacing-xl) 0;
  display: flex;
  justify-content: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo-icon-svg {
  color: var(--color-primary);
  flex-shrink: 0;
}

.logo-text {
  font-family: 'Outfit', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  white-space: nowrap;
}

.sidebar-content {
  flex: 1;
  padding: 0 var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.sidebar.collapsed .sidebar-content {
  padding: 0 var(--spacing-sm);
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-muted);
  letter-spacing: 0.1em;
  padding: 0 var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px var(--spacing-md);
  border-radius: var(--radius-md);
  background-color: transparent;
  color: var(--color-text-secondary);
  transition: all 0.2s ease;
  text-align: left;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  width: 100%;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px 0;
}

.nav-item:hover {
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.nav-item.active {
  background-color: var(--color-primary-pale);
  color: var(--color-primary);
  font-weight: 600;
}

.nav-icon {
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
}

.sidebar-footer {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.sidebar.collapsed .sidebar-footer {
  padding: var(--spacing-lg) var(--spacing-sm);
  align-items: center;
}

.storage-status {
  background-color: var(--color-background);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
}

.storage-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.storage-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.storage-value {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.storage-bar {
  height: 6px;
  background-color: #E5E7EB;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.storage-fill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: 3px;
}

.storage-details {
  font-size: 11px;
  color: var(--color-text-muted);
}

.btn-create-new {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: var(--color-primary);
  color: white;
  padding: 14px;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 15px;
  width: 100%;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.sidebar.collapsed .btn-create-new {
  width: 48px;
  height: 48px;
  padding: 0;
  border-radius: 50%;
}

.btn-create-new:hover {
  opacity: 0.9;
  transform: scale(1.02);
}

@media (max-width: 900px) {
  .sidebar {
    width: 100% !important;
    flex: 0 0 auto !important;
    height: auto;
    padding: var(--spacing-md) 0;
  }

  .sidebar-header, .sidebar-footer, .section-title, .storage-status {
    display: none;
  }

  .sidebar-content {
    padding: 0;
  }

  .sidebar-nav {
    flex-direction: row;
    justify-content: center;
  }

  .nav-item {
    width: auto;
    padding: var(--spacing-sm);
  }

  .nav-label {
    display: none;
  }
}
</style>
