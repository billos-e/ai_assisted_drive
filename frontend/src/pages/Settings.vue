<template>
  <div class="settings-page">
    <div class="settings-container">
      <!-- Section 1: Connection -->
      <div class="settings-section">
        <h2 class="section-title">Connection</h2>
        <div class="section-content">
          <div class="setting-item">
            <div class="setting-label">Google Account</div>
            <div class="setting-value">{{ googleAccount }}</div>
          </div>
          <div class="setting-actions">
            <button class="btn btn-primary" @click="reconnect" :disabled="reconnecting">
              {{ reconnecting ? '🔄 Reconnecting...' : 'Reconnect' }}
            </button>
            <button class="btn btn-secondary" disabled title="Coming soon">
              Change account
              <span class="badge coming-soon">Coming soon</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Section 2: Repository -->
      <div class="settings-section">
        <h2 class="section-title">Repository</h2>
        <div class="section-content">
          <div class="setting-item">
            <div class="setting-label">Root Folder</div>
            <div class="setting-value-with-action">
              <div class="setting-value">{{ rootFolderId }}</div>
              <button class="btn btn-sm btn-secondary" @click="editRootFolder">
                Edit
              </button>
            </div>
          </div>

          <div v-if="editingRootFolder" class="inline-edit">
            <input
              v-model="newRootFolderId"
              type="text"
              placeholder="Enter folder ID or path"
            />
            <button class="btn btn-sm btn-primary" @click="saveRootFolder" :disabled="savingRootFolder">
              Save
            </button>
            <button class="btn btn-sm btn-secondary" @click="editingRootFolder = false">
              Cancel
            </button>
          </div>

          <div class="setting-item">
            <div class="setting-label">Indexing Status</div>
            <div class="setting-value">{{ indexedFilesCount }} files indexed</div>
          </div>

          <div class="setting-actions">
            <button class="btn btn-primary" @click="forceReindex" :disabled="reindexing">
              {{ reindexing ? '🔄 Re-indexing...' : 'Force re-index' }}
            </button>
          </div>

          <div v-if="reindexMessage" class="status-message" :class="reindexStatus">
            {{ reindexMessage }}
          </div>
        </div>
      </div>

      <!-- Section 3: Chat -->
      <div class="settings-section">
        <h2 class="section-title">Chat</h2>
        <div class="section-content">
          <div class="setting-item">
            <div class="setting-label">Model</div>
            <select v-model="selectedModel" class="setting-select">
              <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile</option>
              <option value="llama-3.1-70b-versatile">llama-3.1-70b-versatile</option>
              <option value="mixtral-8x7b-32768">mixtral-8x7b-32768</option>
              <option value="gemma-7b-it">gemma-7b-it</option>
            </select>
            <div class="setting-hint">UI only for now</div>
          </div>

          <div class="setting-item">
            <div class="setting-label">Number of Sources</div>
            <div class="setting-value-with-input">
              <input
                v-model.number="numberOfSources"
                type="number"
                min="1"
                max="20"
                class="setting-number-input"
              />
              <span class="setting-hint">Default: 5, Max: 20</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-label">Response Language</div>
            <select v-model="responseLanguage" class="setting-select">
              <option value="auto">Auto</option>
              <option value="en">English</option>
              <option value="fr">Français</option>
              <option value="es">Español</option>
              <option value="de">Deutsch</option>
            </select>
            <div class="setting-hint">UI only for now</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const googleAccount = ref('user@gmail.com')
const rootFolderId = ref('root-folder-id-123')
const indexedFilesCount = ref(42)
const selectedModel = ref('llama-3.3-70b-versatile')
const numberOfSources = ref(5)
const responseLanguage = ref('auto')

const reconnecting = ref(false)
const editingRootFolder = ref(false)
const newRootFolderId = ref('')
const savingRootFolder = ref(false)
const reindexing = ref(false)
const reindexMessage = ref('')
const reindexStatus = ref('')

const reconnect = async () => {
  reconnecting.value = true
  try {
    // TODO: Implement OAuth2 reconnection logic
    await new Promise(resolve => setTimeout(resolve, 1500))
    alert('Token refreshed successfully')
  } catch (error) {
    console.error('Error reconnecting:', error)
    alert('Error refreshing token')
  } finally {
    reconnecting.value = false
  }
}

const editRootFolder = () => {
  newRootFolderId.value = rootFolderId.value
  editingRootFolder.value = true
}

const saveRootFolder = async () => {
  if (!newRootFolderId.value.trim()) return

  savingRootFolder.value = true
  try {
    // TODO: Implement save logic
    await new Promise(resolve => setTimeout(resolve, 1000))
    rootFolderId.value = newRootFolderId.value
    editingRootFolder.value = false
  } catch (error) {
    console.error('Error saving root folder:', error)
    alert('Error saving root folder')
  } finally {
    savingRootFolder.value = false
  }
}

const forceReindex = async () => {
  reindexing.value = true
  reindexMessage.value = ''
  reindexStatus.value = ''

  try {
    // TODO: Implement force re-index logic
    await new Promise(resolve => setTimeout(resolve, 3000))
    indexedFilesCount.value = 42
    reindexMessage.value = '✓ Re-indexing completed successfully'
    reindexStatus.value = 'success'
    setTimeout(() => {
      reindexMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error('Error re-indexing:', error)
    reindexMessage.value = '✗ Error during re-indexing'
    reindexStatus.value = 'error'
  } finally {
    reindexing.value = false
  }
}
</script>

<style scoped>
.settings-page {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-xl) var(--spacing-lg);
  background-color: var(--color-background);
}

.settings-container {
  max-width: 600px;
}

.settings-section {
  background-color: var(--color-surface);
  border-radius: 8px;
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  border: 1px solid var(--color-border);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.setting-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.setting-value {
  font-size: 14px;
  color: var(--color-text-secondary);
  padding: var(--spacing-sm);
  background-color: var(--color-background);
  border-radius: 4px;
  border: 1px solid var(--color-border);
  word-break: break-word;
}

.setting-value-with-action {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.setting-value-with-action .setting-value {
  flex: 1;
  margin: 0;
}

.setting-value-with-input {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.setting-number-input {
  width: 80px;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
}

.setting-select {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  background-color: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color 0.2s;
}

.setting-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.setting-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-style: italic;
}

.setting-actions {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--color-background);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-border);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.inline-edit {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background-color: var(--color-background);
  border-radius: 4px;
  border: 1px solid var(--color-border);
}

.inline-edit input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
}

.inline-edit input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.status-message {
  padding: var(--spacing-md);
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

.status-message.success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.status-message.error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.badge {
  display: inline-block;
  background-color: #9ca3af;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  margin-left: auto;
}
</style>
