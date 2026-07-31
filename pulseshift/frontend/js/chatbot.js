/**
 * PulseShift Chatbot Widget — Pure Neutral Liquid Glass & Glassmorphism System
 * Source of Truth: design.md
 */

const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000"
  : "https://pulseshift.onrender.com";

class PulseShiftChatbot {
  constructor() {
    this.modal = null;
    this.messagesContainer = null;
    this.inputField = null;
    this.isOpen = false;
    this.chatHistory = [];
    this.init();
  }

  init() {
    if (document.getElementById('pulseshift-chatbot-toggle')) return;
    this.createUI();
    this.attachEventListeners();
  }

  createUI() {
    // 1. Floating Toggle Button (.glass-pill)
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'pulseshift-chatbot-toggle';
    toggleBtn.className = 'chatbot-toggle-btn';
    toggleBtn.setAttribute('title', 'Open Assistant');
    toggleBtn.setAttribute('aria-label', 'Open Assistant');
    toggleBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
    `;

    // 2. Modal Window (.glass-panel)
    const modal = document.createElement('div');
    modal.id = 'pulseshift-chatbot-modal';
    modal.className = 'chatbot-modal';
    modal.innerHTML = `
      <div class="chatbot-header">
        <div class="chatbot-header-info">
          <div class="chatbot-avatar-circle">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="9"></circle>
              <path d="M12 8v8M8 12h8"></path>
            </svg>
          </div>
          <div class="chatbot-header-text">
            <h3>PulseShift Assistant</h3>
            <span>Online • poolside/laguna-s-2.1</span>
          </div>
        </div>
        <button class="chatbot-close-btn" id="pulseshift-chatbot-close" title="Close">✕</button>
      </div>

      <!-- Quick Action Prompt Chips (.glass-pill) -->
      <div class="chatbot-quick-chips">
        <button class="chatbot-chip" data-prompt="Explain entropy formula for this topic">Entropy Formula</button>
        <button class="chatbot-chip" data-prompt="Why is there disagreement on this topic?">Disagreement Drivers</button>
        <button class="chatbot-chip" data-prompt="Summarize the latest news articles">News Briefing</button>
      </div>

      <div class="chatbot-messages" id="pulseshift-chatbot-messages">
        <div class="chatbot-msg ai">
          Hello. I am <strong>PulseShift Assistant</strong> (Model: <code>poolside/laguna-s-2.1:free</code>).<br><br>
          I am monitoring opinion consensus and stance entropy. How can I assist your analysis today?
        </div>
      </div>

      <div class="chatbot-input-area">
        <input type="text" id="pulseshift-chatbot-input" placeholder="Type a query or question..." />
        <button class="chatbot-send-btn" id="pulseshift-chatbot-send" title="Send message">
          <svg viewBox="0 0 24 24">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
          </svg>
        </button>
      </div>
    `;

    document.body.appendChild(toggleBtn);
    document.body.appendChild(modal);

    this.modal = modal;
    this.messagesContainer = document.getElementById('pulseshift-chatbot-messages');
    this.inputField = document.getElementById('pulseshift-chatbot-input');
  }

  attachEventListeners() {
    const toggleBtn = document.getElementById('pulseshift-chatbot-toggle');
    const closeBtn = document.getElementById('pulseshift-chatbot-close');
    const sendBtn = document.getElementById('pulseshift-chatbot-send');
    const chips = this.modal.querySelectorAll('.chatbot-chip');

    toggleBtn.addEventListener('click', () => this.toggle());
    closeBtn.addEventListener('click', () => this.close());
    sendBtn.addEventListener('click', () => this.sendMessage());

    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        const prompt = chip.getAttribute('data-prompt');
        if (prompt) {
          this.inputField.value = prompt;
          this.sendMessage();
        }
      });
    });

    this.inputField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.sendMessage();
    });
  }

  toggle() {
    this.isOpen = !this.isOpen;
    if (this.isOpen) {
      this.modal.classList.add('active');
      this.inputField.focus();
    } else {
      this.modal.classList.remove('active');
    }
  }

  close() {
    this.isOpen = false;
    this.modal.classList.remove('active');
  }

  appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chatbot-msg ${role}`;
    msgDiv.innerHTML = text.replace(/\n/g, '<br>');
    this.messagesContainer.appendChild(msgDiv);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    this.chatHistory.push({ role, text });
  }

  async sendMessage() {
    const text = this.inputField.value.trim();
    if (!text) return;

    this.inputField.value = '';
    this.appendMessage('user', text);

    const typingDiv = document.createElement('div');
    typingDiv.className = 'chatbot-msg ai';
    typingDiv.innerHTML = '<em>Processing request...</em>';
    this.messagesContainer.appendChild(typingDiv);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;

    const apiUrl = `${API_BASE}/chat`;

    try {
      const activeTopic = window.currentTopicData?.topic?.title || null;
      const res = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          topic_title: activeTopic,
          context: window.currentTopicData || {}
        })
      });

      this.messagesContainer.removeChild(typingDiv);

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data = await res.json();
      this.appendMessage('ai', data.reply || 'No response returned.');
    } catch (err) {
      if (typingDiv.parentNode) {
        this.messagesContainer.removeChild(typingDiv);
      }
      this.appendMessage('ai', `⚠️ Connection error: ${err.message}`);
    }
  }
}

function initPulseShiftChatbot() {
  if (!window.pulseshiftChatbot) {
    window.pulseshiftChatbot = new PulseShiftChatbot();
  }
}

if (document.readyState === 'complete' || document.readyState === 'interactive') {
  initPulseShiftChatbot();
} else {
  document.addEventListener('DOMContentLoaded', initPulseShiftChatbot);
}
