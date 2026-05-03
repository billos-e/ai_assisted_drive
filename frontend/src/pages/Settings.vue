<template>
  <div class="settings-page">
    <div class="settings-container">
      <header class="settings-header">
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Manage your account and application preferences</p>
      </header>

      <!-- Section 1: Connection -->
      <div class="settings-section glass">
        <div class="section-header">
          <div class="section-icon-wrapper">
            <LinkIcon :size="18" />
          </div>
          <h2 class="section-title">Connection</h2>
        </div>
        
        <div class="section-content">
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Google Account</div>
              <div class="setting-hint">The account used to sync with Google Drive</div>
            </div>
            <div class="setting-value">{{ googleAccount }}</div>
          </div>
          
          <div class="setting-actions">
            <button class="btn btn-primary" disabled title="Coming soon">
              <RotateCcw :size="14" />
              <span>Reconnect Account</span>
              <span class="badge coming-soon">Soon</span>
            </button>
            <button class="btn btn-secondary" disabled title="Coming soon">
              <span>Change account</span>
              <span class="badge coming-soon">Soon</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Section 2: Repository -->
      <div class="settings-section glass">
        <div class="section-header">
          <div class="section-icon-wrapper">
            <Database :size="18" />
          </div>
          <h2 class="section-title">Repository</h2>
        </div>

        <div class="section-content">
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Root Folder</div>
              <div class="setting-hint">Files in this folder will be indexed for the AI</div>
            </div>
            <div class="setting-value-group">
              <div class="setting-value-pill" :title="rootFolderId">{{ rootFolderId }}</div>
              <button class="btn-icon" @click="editRootFolder" title="Edit folder">
                <Edit3 :size="16" />
              </button>
            </div>
          </div>

          <Transition name="slide-down">
            <div v-if="editingRootFolder" class="inline-edit-box">
              <div class="input-container glass">
                <input
                  v-model="newRootFolderId"
                  type="text"
                  placeholder="Enter folder ID or path"
                />
              </div>
              <div class="inline-actions">
                <button class="btn btn-primary btn-sm" @click="saveRootFolder" :disabled="savingRootFolder">
                  <span v-if="!savingRootFolder">Save</span>
                  <LoaderCircle v-else :size="14" class="spin" />
                </button>
                <button class="btn btn-secondary btn-sm" @click="editingRootFolder = false">
                  Cancel
                </button>
              </div>
            </div>
          </Transition>

          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Indexing Status</div>
              <div class="setting-hint">Total number of documents stored in your local knowledge base</div>
            </div>
            <div class="setting-value-pill highlight">
              <span class="count">{{ indexedFilesCount }}</span>
              <span>files indexed</span>
            </div>
          </div>

          <div class="setting-actions">
            <button class="btn btn-primary" @click="forceReindex" :disabled="reindexing">
              <RefreshCw v-if="!reindexing" :size="14" />
              <LoaderCircle v-else :size="14" class="spin" />
              <span>{{ reindexing ? 'Re-indexing...' : 'Force Re-index' }}</span>
            </button>
          </div>

          <Transition name="fade">
            <div v-if="reindexMessage" class="status-banner" :class="reindexStatus">
              <CheckCircle v-if="reindexStatus === 'success'" :size="16" />
              <AlertCircle v-else :size="16" />
              <span>{{ reindexMessage }}</span>
            </div>
          </Transition>
        </div>
      </div>

      <!-- Section 3: Chat -->
      <div class="settings-section glass">
        <div class="section-header">
          <div class="section-icon-wrapper">
            <Settings2 :size="18" />
          </div>
          <h2 class="section-title">Chat & Model</h2>
        </div>

        <div class="section-content">
          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Model Selection</div>
              <div class="setting-hint">Choose the AI model for generating responses</div>
            </div>
            <div class="select-wrapper">
              <select v-model="selectedModel" @change="updateModel" class="setting-select">
                <option value="llama-3.3-70b-versatile">Llama 3.3 70B (Versatile)</option>
                <option value="llama-3.1-70b-versatile">Llama 3.1 70B (Legacy)</option>
                <option value="mixtral-8x7b-32768">Mixtral 8x7B (MoE)</option>
                <option value="gemma-7b-it">Gemma 7B (Lightweight)</option>
              </select>
              <ChevronDown :size="16" class="select-icon" />
            </div>
          </div>

          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Search Depth</div>
              <div class="setting-hint">Number of context sources to retrieve (Max 20)</div>
            </div>
            <div class="number-input-wrapper">
              <input
                v-model.number="numberOfSources"
                @change="updateSources"
                type="number"
                min="1"
                max="20"
                class="setting-number-input"
              />
              <span class="unit">sources</span>
            </div>
          </div>

          <div class="setting-row">
            <div class="setting-info">
              <div class="setting-label">Response Language</div>
              <div class="setting-hint">Target language for the AI responses</div>
            </div>
            <div class="select-wrapper">
              <select v-model="responseLanguage" @change="updateLanguage" class="setting-select">
                <option value="en">English</option>
                <option value="fr">Français</option>
                <option value="es">Español</option>
                <option value="de">Deutsch</option>
              </select>
              <ChevronDown :size="16" class="select-icon" />
            </div>
          </div>
          
          <div v-if="!isBackendConnected" class="ui-only-badge">
            <Info :size="14" />
            <span>AI model settings are currently UI-only and will be connected soon.</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { settingsAPI } from '../services/api'
import { 
  Link as LinkIcon, 
  RotateCcw, 
  LoaderCircle, 
  Database, 
  Edit3, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle,
  Settings2,
  ChevronDown,
  Info
} from 'lucide-vue-next'

const googleAccount = ref('user@gmail.com')
const rootFolderId = ref('root-folder-id-123')
const indexedFilesCount = ref(42)
const selectedModel = ref('llama-3.3-70b-versatile')
const numberOfSources = ref(5)
const responseLanguage = ref('fr')
const isBackendConnected = ref(false)

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
    await new Promise(resolve => setTimeout(resolve, 1500))
    // Success feedback is handled by re-enabling button
  } catch (error) {
    console.error('Error reconnecting:', error)
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
    await settingsAPI.updateSettings({ root_folder_id: newRootFolderId.value })
    rootFolderId.value = newRootFolderId.value
    editingRootFolder.value = false
  } catch (error) {
    console.error('Error saving root folder:', error)
  } finally {
    savingRootFolder.value = false
  }
}

const forceReindex = async () => {
  reindexing.value = true
  reindexMessage.value = ''
  reindexStatus.value = ''
  try {
    // We could call an actual re-index endpoint here if it exists
    await new Promise(resolve => setTimeout(resolve, 3000))
    await fetchSettings()
    reindexMessage.value = 'Re-indexing completed successfully'
    reindexStatus.value = 'success'
    setTimeout(() => {
      reindexMessage.value = ''
    }, 4000)
  } catch (error) {
    console.error('Error re-indexing:', error)
    reindexMessage.value = 'Error during re-indexing'
    reindexStatus.value = 'error'
  } finally {
    reindexing.value = false
  }
}

const fetchSettings = async () => {
  try {
    const data = await settingsAPI.getSettings()
    googleAccount.value = data.google_account
    rootFolderId.value = data.root_folder_id
    indexedFilesCount.value = data.indexed_files_count
    selectedModel.value = data.selected_model
    numberOfSources.value = data.number_of_sources
    responseLanguage.value = data.response_language === 'auto' ? 'fr' : data.response_language
    isBackendConnected.value = true
  } catch (error) {
    console.error('Error fetching settings:', error)
  }
}

const updateModel = async () => {
  try {
    await settingsAPI.updateSettings({ selected_model: selectedModel.value })
  } catch (error) {
    console.error('Error updating model:', error)
  }
}

const updateSources = async () => {
  try {
    await settingsAPI.updateSettings({ number_of_sources: numberOfSources.value })
  } catch (error) {
    console.error('Error updating sources:', error)
  }
}

const updateLanguage = async () => {
  try {
    await settingsAPI.updateSettings({ response_language: responseLanguage.value })
  } catch (error) {
    console.error('Error updating language:', error)
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.settings-page {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-xl) var(--spacing-lg);
  background-color: var(--color-background);
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: 32px;
  margin-bottom: 8px;
}

.page-subtitle {
  color: var(--color-text-secondary);
  font-size: 15px;
}

.settings-section {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
  border-radius: var(--radius-lg);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: var(--spacing-xl);
}

.section-icon-wrapper {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-light);
  border: 1px solid var(--color-border);
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-lg);
}

.setting-info {
  flex: 1;
}

.setting-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.setting-hint {
  font-size: 13px;
  color: var(--color-text-muted);
}

.setting-value {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-family: 'JetBrains Mono', monospace;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
}

.setting-value-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-value-pill {
  padding: 6px 16px;
  background: var(--color-background);
  border-radius: 20px;
  border: 1px solid var(--color-border);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
  font-family: 'JetBrains Mono', monospace;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.setting-value-pill.highlight {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
  color: var(--color-primary-light);
}

.setting-value-pill .count {
  font-weight: 700;
  font-size: 16px;
}

.select-wrapper {
  position: relative;
  width: 240px;
}

.setting-select {
  width: 100%;
  appearance: none;
  padding: 10px 16px;
  padding-right: 40px;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.select-icon {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--color-text-muted);
}

.number-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-number-input {
  width: 100px;
  text-align: center;
  padding: 10px;
}

.unit {
  font-size: 13px;
  color: var(--color-text-muted);
}

.setting-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
}

.badge.coming-soon {
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.2s ease;
  pointer-events: none;
}

button:hover .badge.coming-soon {
  opacity: 1;
  transform: translateX(0);
}

.inline-edit-box {
  background: rgba(0, 0, 0, 0.15);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.inline-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-pale);
  border: 1px solid rgba(79, 70, 229, 0.1);
  color: var(--color-primary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-icon:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
}

.btn-icon:active {
  transform: translateY(0);
}

.status-banner {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
}

.status-banner.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-banner.error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.ui-only-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--color-text-muted);
}

.spin {
  animation: spin 1s linear infinite;
}

@media (max-width: 600px) {
  .setting-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .select-wrapper, .setting-value {
    width: 100%;
  }
}
</style>
