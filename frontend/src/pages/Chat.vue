<template>
  <div class="chat-page">
    <!-- Warning banner -->
    <div v-if="!hasIndexedFiles" class="warning-banner">
      <CircleAlert :size="16" />
      <span>No files indexed yet — go to the Repository to upload files</span>
    </div>

    <!-- Messages area -->
    <div class="messages-container" ref="messagesContainer">
      <!-- Empty state -->
      <div v-if="messages.length === 0" class="empty-chat-state">
        <div class="welcome-message">
          <h2>Ask anything about your files</h2>
          <p>Upload documents in the Repository to get started</p>
        </div>
        <div class="example-chips">
          <button
            v-for="(example, index) in exampleQuestions"
            :key="index"
            class="chip"
            @click="sendMessage(example)"
          >
            {{ example }}
          </button>
        </div>
      </div>

      <!-- Messages -->
      <template v-else>
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="message.role"
        >
          <div class="message-bubble">
            <div class="message-content">{{ message.content }}</div>
            <div v-if="message.sources && message.sources.length > 0" class="message-sources">
              Sources: {{ message.sources.join(', ') }}
            </div>
          </div>
        </div>

        <!-- Thinking indicator -->
        <div v-if="isWaiting" class="message assistant">
          <div class="thinking-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </template>
    </div>

    <!-- Input area -->
    <div class="input-area">
      <div class="input-wrapper">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="Type your question..."
          @keyup.enter="sendMessage(inputMessage)"
          :disabled="isWaiting || !hasIndexedFiles"
        />
        <button
          class="btn btn-primary"
          @click="sendMessage(inputMessage)"
          :disabled="!inputMessage.trim() || isWaiting || !hasIndexedFiles"
        >
          Send
        </button>
        <button
          v-if="messages.length > 0"
          class="btn btn-secondary"
          @click="clearConversation"
          :disabled="isWaiting"
        >
          <Trash2 :size="16" />
          <span>Clear</span>
        </button>
      </div>
    </div>

    <!-- Clear confirmation modal -->
    <div v-if="showClearConfirm" class="modal-overlay" @click="showClearConfirm = false">
      <div class="modal" @click.stop>
        <h3>Clear conversation?</h3>
        <p>This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-primary" @click="confirmClear">Yes, clear</button>
          <button class="btn btn-secondary" @click="showClearConfirm = false">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { CircleAlert, Trash2 } from 'lucide-vue-next'
import { chatAPI } from '../services/api'

const messages = ref([])
const inputMessage = ref('')
const isWaiting = ref(false)
const showClearConfirm = ref(false)
const messagesContainer = ref(null)
const hasIndexedFiles = ref(true) // TODO: Check actual indexing status from backend
const currentTopK = ref(5)

const exampleQuestions = [
  'What is the main topic?',
  'Summarize the key points',
  'What are the next steps?'
]

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async (message = null) => {
  const text = message || inputMessage.value.trim()
  if (!text || isWaiting.value) return

  // Add user message
  messages.value.push({
    role: 'user',
    content: text,
    sources: []
  })

  messages.value.push({
    role: 'assistant',
    content: '',
    sources: []
  })

  inputMessage.value = ''
  isWaiting.value = true

  await scrollToBottom()

  try {
    let assistantMessage = ''

    // Stream response
    await chatAPI.streamChat(
      text,
      messages.value
        .filter(m => m.role !== 'assistant' || m.content.length > 0)
        .map(m => ({ role: m.role, content: m.content })),
      currentTopK.value,
      (chunk) => {
        assistantMessage += chunk
        messages.value[messages.value.length - 1].content = assistantMessage
        scrollToBottom()
      }
    )

    messages.value[messages.value.length - 1].content = assistantMessage

    await scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value[messages.value.length - 1].content = 'Sorry, there was an error processing your request. Please try again.'
  } finally {
    isWaiting.value = false
  }
}

const clearConversation = () => {
  showClearConfirm.value = true
}

const confirmClear = () => {
  messages.value = []
  inputMessage.value = ''
  showClearConfirm.value = false
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 0;
  height: 100%;
  overflow: hidden;
  align-self: stretch;
}

.warning-banner {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: #fef3c7;
  color: #92400e;
  font-size: 13px;
  font-weight: 500;
  border-bottom: 1px solid #fcd34d;
  display: flex;
  align-items: center;
  gap: 8px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  background-color: var(--color-background);
  width: 100%;
  min-width: 0;
}

.empty-chat-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--spacing-lg);
}

.welcome-message {
  text-align: center;
  color: var(--color-text-secondary);
}

.welcome-message h2 {
  font-size: 24px;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-primary);
}

.welcome-message p {
  font-size: 14px;
}

.example-chips {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  width: 100%;
  max-width: 300px;
}

.chip {
  padding: var(--spacing-md);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: var(--color-text-primary);
}

.chip:hover {
  border-color: var(--color-primary);
  background-color: var(--color-primary);
  color: white;
}

.message {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: var(--spacing-md);
  border-radius: 8px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  min-width: 0;
}

.message.user .message-bubble {
  background-color: var(--color-primary);
  color: white;
}

.message.assistant .message-bubble {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.message-content {
  font-size: 14px;
  line-height: 1.5;
}

.message-sources {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: var(--spacing-sm);
  font-style: italic;
}

.message.user .message-sources {
  color: rgba(255, 255, 255, 0.7);
}

.thinking-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  height: 20px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-primary);
  animation: bounce 1.4s infinite;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-6px);
  }
}

.input-area {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  background-color: var(--color-surface);
  flex-shrink: 0;
  width: 100%;
}

.input-wrapper {
  display: flex;
  gap: var(--spacing-md);
  max-width: 100%;
  width: 100%;
}

.input-wrapper input {
  flex: 1;
  padding: 10px var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.input-wrapper input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.input-wrapper input:disabled {
  background-color: var(--color-background);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.btn {
  padding: 10px 16px;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
  font-weight: 500;
  white-space: nowrap;
  display: inline-flex;
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background-color: var(--color-surface);
  border-radius: 8px;
  padding: var(--spacing-lg);
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal h3 {
  font-size: 18px;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-primary);
}

.modal p {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-md);
}

.modal-actions .btn {
  flex: 1;
}

@media (max-width: 900px) {
  .input-wrapper {
    flex-direction: column;
  }

  .message-bubble {
    max-width: 100%;
  }
}
</style>
