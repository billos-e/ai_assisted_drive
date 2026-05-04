<template>
  <div class="chat-page">
    <!-- Warning banner -->
    <Transition name="slide-down">
      <div v-if="!hasIndexedFiles" class="warning-banner">
        <CircleAlert :size="16" />
        <span>Aucun fichier indexé — allez dans le Répertoire pour en ajouter</span>
      </div>
    </Transition>

    <!-- Messages area -->
    <div class="messages-container" ref="messagesContainer">
      <!-- Empty state -->
      <div v-if="messages.length === 0" class="empty-chat-state">
        <div class="hero-section">
          <h1 class="salutation">Bienvenue</h1>
          <h2 class="main-question">Comment puis-je vous aider aujourd'hui ?</h2>
          <p class="instruction-text">Explorez votre base de documents avec l'IA ou posez directement votre question ci-dessous.</p>
        </div>
        
        <div class="suggestions-grid">
          <button
            v-for="(example, index) in exampleQuestions"
            :key="index"
            class="suggestion-card"
            @click="sendMessage(example.text)"
          >
            <span class="suggestion-text">{{ example.text }}</span>
            <div class="suggestion-icon">
              <component :is="example.icon" :size="20" :stroke-width="1.5" />
            </div>
          </button>
        </div>

        <!-- Central Input for empty state -->
        <div class="central-input-container">
          <div class="main-input-bar">
            <input
              v-model="inputMessage"
              type="text"
              placeholder="Posez une question sur vos documents..."
              @keyup.enter="sendMessage(inputMessage)"
              :disabled="isWaiting || !hasIndexedFiles"
            />
            <button
              class="send-btn-circle"
              @click="sendMessage(inputMessage)"
              :disabled="!inputMessage.trim() || isWaiting || !hasIndexedFiles"
            >
              <ArrowRight :size="20" />
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <template v-else>
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message-wrapper"
          :class="message.role"
        >
          <div class="avatar-small" :class="message.role">
            <CircleUser v-if="message.role === 'user'" :size="14" />
            <Sparkles v-else :size="14" />
          </div>
          
          <div class="message-bubble-container">
            <div class="message-bubble">
              <!-- If assistant and waiting and content is empty, show thinking dots after delay -->
              <div v-if="message.role === 'assistant' && !message.content && isWaiting && isResponseDelayed" class="thinking-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
              <div v-else class="message-content markdown-content" v-html="formatMessageContent(message.content)"></div>
              
              <div v-if="message.sources && message.sources.length > 0" class="message-sources-inline">
                <div class="source-tooltip-container">
                  <button class="source-icon-btn" title="Voir les sources">
                    <LinkIcon :size="14" />
                  </button>
                  <div class="source-tooltip glass">
                    <div class="tooltip-header">Sources</div>
                    <div 
                      v-for="(source, idx) in message.sources" 
                      :key="`${source.source_path}-${idx}`" 
                      class="tooltip-item"
                      @click="openSource(source)"
                      :title="'Ouvrir ' + (source.file_name || truncatePath(source.source_path))"
                    >
                      <FileText :size="12" />
                      <span>{{ source.file_name || truncatePath(source.source_path) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>


      </template>
    </div>

    <!-- Input area (only shown when there are messages) -->
    <div v-if="messages.length > 0" class="input-area-floating">
      <div class="input-wrapper">
        <div class="input-upper-actions">
          <button
            class="clear-btn-visible"
            @click="clearConversation"
            :disabled="isWaiting"
            title="Vider la conversation"
          >
            <Trash2 :size="16" />
            <span>Vider la conversation</span>
          </button>
        </div>
        <div class="main-input-bar">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Posez une question sur vos documents..."
            @keyup.enter="sendMessage(inputMessage)"
            :disabled="isWaiting || !hasIndexedFiles"
          />
          <button
            class="send-btn-circle"
            @click="sendMessage(inputMessage)"
            :disabled="!inputMessage.trim() || isWaiting || !hasIndexedFiles"
          >
            <ArrowRight :size="20" />
          </button>
        </div>
      </div>
    </div>

    <!-- Clear confirmation modal -->
    <Transition name="fade">
      <div v-if="showClearConfirm" class="modal-overlay" @click="showClearConfirm = false">
        <div class="modal glass" @click.stop>
          <div class="modal-icon warning">
            <Trash2 :size="24" />
          </div>
          <h3>Effacer la conversation ?</h3>
          <p>Cela supprimera définitivement l'historique de votre chat actuel. Cette action est irréversible.</p>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showClearConfirm = false">Annuler</button>
            <button class="btn btn-primary danger" @click="confirmClear">Effacer le chat</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { 
  CircleAlert, Trash2, Sparkles, Send, CircleUser, BookOpen, 
  FileText, RotateCcw, MessageSquare, Link as LinkIcon,
  ArrowRight, Search, MessageCircle
} from 'lucide-vue-next'
import { chatAPI, driveAPI } from '../services/api'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const messages = ref([])
const inputMessage = ref('')
const isWaiting = ref(false)
const showClearConfirm = ref(false)
const messagesContainer = ref(null)
const hasIndexedFiles = ref(true) // TODO: Check actual indexing status from backend
const currentTopK = ref(5)
const isResponseDelayed = ref(false)
let thinkingTimeout = null

const CHAT_HISTORY_KEY = 'chat_history_v1'

const exampleQuestions = [
  { text: 'Quelles sont les informations clés de mes derniers documents ?', icon: Sparkles },
  { text: 'Aide-moi à retrouver un fichier spécifique dans mon drive', icon: Search },
  { text: 'Peux-tu me résumer le contenu de mon dossier principal ?', icon: BookOpen }
]

marked.setOptions({
  gfm: true,
  breaks: true
})

const formatMessageContent = (content = '') => {
  const renderedHtml = marked.parse(content)
  return DOMPurify.sanitize(renderedHtml)
}

const truncatePath = (path) => {
  if (!path) return ''
  const parts = path.split('/')
  return parts[parts.length - 1]
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

const openSource = async (source) => {
  try {
    if (source.file_id) {
      const response = await driveAPI.openFile(source.file_id)
      if (response && response.url) {
        window.open(response.url, '_blank')
      }
    } else {
      console.warn("No file_id available for source:", source)
    }
  } catch (error) {
    console.error('Error opening source:', error)
  }
}

const saveChatHistory = () => {
  try {
    const historyData = {
      version: 1,
      timestamp: new Date().toISOString(),
      messages: messages.value.map(m => ({
        role: m.role,
        content: m.content,
        sources: m.sources || [],
        timestamp: m.timestamp
      }))
    }
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(historyData))
  } catch (error) {
    console.error('Failed to save chat history:', error)
  }
}

const loadChatHistory = () => {
  try {
    const stored = localStorage.getItem(CHAT_HISTORY_KEY)
    if (stored) {
      const historyData = JSON.parse(stored)
      if (historyData.version === 1) {
        messages.value = (historyData.messages || []).map(m => ({
          role: m.role,
          content: m.content,
          sources: m.sources || [],
          timestamp: m.timestamp || new Date().toISOString()
        }))
      }
    }
  } catch (error) {
    console.error('Failed to load chat history:', error)
  }
}

const sendMessage = async (message = null) => {
  const text = message || inputMessage.value.trim()
  if (!text || isWaiting.value) return
  
  // Clear any previous thinking timeout
  if (thinkingTimeout) clearTimeout(thinkingTimeout)
  isResponseDelayed.value = false

  const timestamp = new Date().toISOString()

  messages.value.push({
    role: 'user',
    content: text,
    sources: [],
    timestamp
  })

  messages.value.push({
    role: 'assistant',
    content: '',
    sources: [],
    timestamp: new Date().toISOString()
  })

  inputMessage.value = ''
  isWaiting.value = true
  
  // Start a small delay before showing thinking dots to avoid flickering
  thinkingTimeout = setTimeout(() => {
    isResponseDelayed.value = true
  }, 500)

  await scrollToBottom()
  saveChatHistory()

  try {
    let assistantMessage = ''

    const result = await chatAPI.streamChat(
      text,
      messages.value
        .filter(m => m.role !== 'assistant' || m.content.length > 0)
        .slice(0, -1)
        .map(m => ({ role: m.role, content: m.content })),
      currentTopK.value,
      (chunk) => {
        assistantMessage += chunk
        messages.value[messages.value.length - 1].content = assistantMessage
        scrollToBottom()
      }
    )

    const assistantIndex = messages.value.length - 1
    messages.value[assistantIndex].content = result.text || assistantMessage
    messages.value[assistantIndex].sources = result.sources || []

    await scrollToBottom()
    saveChatHistory()
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value[messages.value.length - 1].content = "Désolé, une erreur s'est produite lors du traitement de votre demande. Veuillez réessayer."
    saveChatHistory()
  } finally {
    isWaiting.value = false
    isResponseDelayed.value = false
    if (thinkingTimeout) clearTimeout(thinkingTimeout)
  }
}

const clearConversation = () => {
  showClearConfirm.value = true
}

const confirmClear = () => {
  messages.value = []
  inputMessage.value = ''
  showClearConfirm.value = false
  try {
    localStorage.removeItem(CHAT_HISTORY_KEY)
  } catch (error) {
    console.error('Failed to clear chat history:', error)
  }
}

onMounted(() => {
  loadChatHistory()
  scrollToBottom()
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #F9FAFB;
}

.warning-banner {
  padding: var(--spacing-sm) var(--spacing-lg);
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  font-size: 13px;
  font-weight: 500;
  border-bottom: 1px solid rgba(245, 158, 11, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-xl) var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

.empty-chat-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 40px 20px;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  margin-bottom: 48px;
}

.salutation {
  font-size: 36px;
  font-weight: 700;
  color: #374151;
  margin-bottom: 8px;
}

.main-question {
  font-size: 32px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
  line-height: 1.2;
}

.instruction-text {
  font-size: 14px;
  color: #6B7280;
  font-weight: 400;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  width: 100%;
  max-width: 860px; /* Narrower than input for visual balance */
  margin-bottom: 40px;
}

.suggestion-card {
  background: white;
  border: 1px solid #F3F4F6;
  border-radius: 20px;
  padding: 24px;
  height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: left;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

.suggestion-card:hover {
  border-color: rgba(124, 58, 237, 0.3);
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.suggestion-card:hover .suggestion-icon {
  background: rgba(124, 58, 237, 0.1);
  color: #7C3AED;
  transform: scale(1.1);
}

.suggestion-text {
  font-size: 15px;
  font-weight: 500;
  color: #374151;
  line-height: 1.4;
}

.suggestion-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #F9FAFB;
  color: #9CA3AF;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.central-input-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.main-input-bar {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 40px;
  padding: 8px 10px 8px 30px;
  width: 100%;
  max-width: 960px; /* Wider than the suggestions grid */
  display: flex;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

.main-input-bar input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px 0;
  font-size: 16px;
  color: #1F2937;
  outline: none;
  box-shadow: none !important;
}

.main-input-bar input::placeholder {
  color: #D1D5DB;
  font-weight: 300;
}

.send-btn-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #7C3AED; /* Vibrant Violet */
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0;
  flex-shrink: 0;
}

.send-btn-circle:hover:not(:disabled) {
  background: #6D28D9;
  transform: scale(1.05);
}

.send-btn-circle:disabled {
  opacity: 0.5;
  background: #E5E7EB;
  color: #9CA3AF;
}

.message-wrapper {
  display: flex;
  gap: 16px;
  max-width: 800px;
  width: 100%;
  align-self: center;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.avatar-small {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4px;
}

.avatar-small.user {
  background: var(--color-surface-hover);
  color: var(--color-text-primary);
}

.avatar-small.assistant {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-primary);
}

.message-bubble-container {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.user .message-bubble-container {
  align-items: flex-end;
}

.message-bubble {
  padding: 16px 20px;
  border-radius: var(--radius-lg);
  font-size: 15px;
  line-height: 1.6;
  position: relative;
  max-width: 100%;
}

.user .message-bubble {
  background: #f3f4f6;
  color: var(--color-text-primary);
  border-bottom-right-radius: 4px;
}

.assistant .message-bubble {
  background: transparent;
  color: var(--color-text-primary);
}

.message-content :deep(p) { margin-bottom: 12px; }
.message-content :deep(p:last-child) { margin-bottom: 0; }
.message-content :deep(pre) {
  background: rgba(0, 0, 0, 0.2);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}
.message-content :deep(code) {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
}
.user .message-content :deep(code) { background: rgba(255, 255, 255, 0.1); }

.message-sources-inline {
  display: flex;
  margin-top: 8px;
  justify-content: flex-start;
}

.source-tooltip-container {
  position: relative;
  display: inline-flex;
}

.source-icon-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  padding: 4px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.source-icon-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-primary);
}

.source-tooltip {
  position: absolute;
  bottom: 100%;
  left: 0;
  margin-bottom: 8px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 8px;
  min-width: 200px;
  box-shadow: var(--shadow-lg);
  opacity: 0;
  visibility: hidden;
  transform: translateY(4px);
  transition: all 0.2s;
  z-index: 50;
}

.source-tooltip-container:hover .source-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.tooltip-header {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  margin-bottom: 8px;
  padding: 0 4px;
}

.tooltip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tooltip-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-primary);
}

.thinking-bubble {
  padding: 12px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  border-bottom-left-radius: 4px;
  display: flex;
  gap: 6px;
  align-items: center;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-primary);
  animation: bounce 1.4s infinite;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.3; }
  40% { transform: translateY(-4px); opacity: 1; }
}

.input-area-floating {
  padding: 24px;
  background: linear-gradient(to top, #F9FAFB 70%, transparent);
  flex-shrink: 0;
  z-index: 10;
  width: 100%;
}

.input-upper-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
  width: 100%;
}

.clear-btn-visible {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  color: #9CA3AF;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
}

.clear-btn-visible:hover:not(:disabled) {
  color: #EF4444;
  background: #FEF2F2;
}

.clear-btn-visible span {
  opacity: 0;
  transform: translateX(4px);
  transition: all 0.2s;
}

.clear-btn-visible:hover span {
  opacity: 1;
  transform: translateX(0);
}

.input-area-floating .main-input-bar {
  max-width: 100%;
}

.thinking-dots {
  display: flex;
  gap: 4px;
  padding: 8px 0;
  align-items: center;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  max-width: 400px;
  width: 100%;
  padding: 32px;
  border-radius: var(--radius-lg);
  text-align: center;
}

.modal-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.modal-icon.warning {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.modal h3 {
  font-size: 20px;
  margin-bottom: 12px;
}

.modal p {
  color: var(--color-text-secondary);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 24px;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.modal-actions .btn {
  flex: 1;
}

.btn.danger {
  background: var(--color-error);
  color: white;
}

/* Transitions */
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from, .slide-down-leave-to { transform: translateY(-20px); opacity: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .message-bubble { max-width: 90%; }
  .welcome-container { padding: 24px; }
  .welcome-message h2 { font-size: 22px; }
}
</style>
