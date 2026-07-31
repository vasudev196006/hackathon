/**
 * PulseShift Liquid Glass AI Chatbot Component
 * Powered by Google Gemini AI
 */
(function () {
  class PulseShiftGeminiChatbot {
    constructor() {
      this.isOpen = false;
      this.isMinimized = false;
      this.isProcessing = false;
      this.activeTopicTitle = null;
      this.activeTopicId = null;
      this.chatHistory = [];

      this.init();
    }

    init() {
      if (document.getElementById('chatbot-trigger-btn')) return;
      this.renderWidget();
      this.bindEvents();
      this.detectActiveTopic();
    }

    renderWidget() {
      // 1. Floating Trigger Button
      const btn = document.createElement('button');
      btn.id = 'chatbot-trigger-btn';
      btn.className = 'chatbot-trigger-btn';
      btn.setAttribute('aria-label', 'Open AI Assistant');
      btn.innerHTML = `
        <img src="/static/assets/pulseshift_ai_avatar.png" alt="PulseShift AI Logo" class="chatbot-btn-avatar">
        <span class="chatbot-badge-pulse"></span>
      `;
      document.body.appendChild(btn);

      // 2. Chat Window Container
      const win = document.createElement('div');
      win.id = 'chatbot-window';
      win.className = 'chatbot-window';
      win.innerHTML = `
        <div class="chatbot-header">
          <div class="chat-header-info">
            <div class="chat-header-avatar">
              <img src="/static/assets/pulseshift_ai_avatar.png" alt="PulseShift AI Avatar">
            </div>
            <div class="chat-header-text">
              <h4>PulseShift AI</h4>
              <p>Tencent Hunyuan 3 (OpenRouter)</p>
            </div>
          </div>
          <div class="chat-header-actions">
            <button class="chat-action-btn" id="chat-clear-btn" title="Clear Chat"><i class="fa-solid fa-rotate-left"></i></button>
            <button class="chat-action-btn" id="chat-min-btn" title="Minimize"><i class="fa-solid fa-minus"></i></button>
            <button class="chat-action-btn" id="chat-close-btn" title="Close"><i class="fa-solid fa-xmark"></i></button>
          </div>
        </div>

        <div id="chat-topic-banner" class="chat-topic-banner" style="display: none;">
          <i class="fa-solid fa-bullseye"></i>
          <span id="chat-topic-banner-text">Active Topic: General</span>
        </div>

        <div class="chatbot-body" id="chatbot-body">
          <div class="chat-row ai-row">
            <div class="chat-avatar-mini"><img src="/static/assets/pulseshift_ai_avatar.png" alt="AI"></div>
            <div class="chat-bubble">
              Welcome to <strong>PulseShift Intelligence</strong>! 📰<br>
              Powered by <strong>Tencent Hunyuan 3</strong> via OpenRouter. Ask me to synthesize press coverage, analyze media friction, or explain public stance dynamics!
            </div>
          </div>
        </div>

        <div class="chatbot-suggestions">
          <button class="suggestion-chip" data-question="Synthesize recent news articles and press reports"><i class="fa-solid fa-newspaper"></i> Media Coverage</button>
          <button class="suggestion-chip" data-question="Executive Policy Briefing based on news & stance data"><i class="fa-solid fa-landmark"></i> Policy Briefing</button>
          <button class="suggestion-chip" data-question="Explain Shannon Entropy H(P) math & opinion dispersion"><i class="fa-solid fa-calculator"></i> Entropy Math</button>
          <button class="suggestion-chip" data-question="Why are people divided compared to news reports?"><i class="fa-solid fa-scale-balanced"></i> Media Friction</button>
        </div>

        <div class="chatbot-footer">
          <form id="chatbot-form" class="chatbot-form">
            <input type="text" id="chatbot-input" class="chatbot-input" placeholder="Ask PulseShift AI..." autocomplete="off">
            <button type="submit" class="chatbot-send-btn"><i class="fa-solid fa-paper-plane"></i></button>
          </form>
        </div>
      `;
      document.body.appendChild(win);
    }

    bindEvents() {
      const btn = document.getElementById('chatbot-trigger-btn');
      const closeBtn = document.getElementById('chat-close-btn');
      const minBtn = document.getElementById('chat-min-btn');
      const clearBtn = document.getElementById('chat-clear-btn');
      const form = document.getElementById('chatbot-form');

      btn.addEventListener('click', () => this.toggleChat());
      closeBtn.addEventListener('click', () => this.closeChat());
      minBtn.addEventListener('click', () => this.minimizeChat());
      clearBtn.addEventListener('click', () => this.clearChat());

      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const input = document.getElementById('chatbot-input');
        const text = input.value.trim();
        if (text && !this.isProcessing) {
          input.value = '';
          this.handleSendMessage(text);
        }
      });

      document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
          const q = chip.getAttribute('data-question');
          if (q && !this.isProcessing) {
            this.openChat();
            this.handleSendMessage(q);
          }
        });
      });
    }

    detectActiveTopic() {
      if (window.currentTopicData && window.currentTopicData.topic) {
        this.activeTopicTitle = window.currentTopicData.topic.title;
        this.activeTopicId = window.currentTopicData.topic.id;
      }
      if (!this.activeTopicTitle) {
        const urlParams = new URLSearchParams(window.location.search);
        const tParam = urlParams.get('topic') || urlParams.get('q');
        if (tParam) this.activeTopicTitle = tParam;
      }
      if (!this.activeTopicTitle) {
        const titleEl = document.getElementById('topic-display-title');
        if (titleEl) {
          const txt = titleEl.innerText.replace("Analyzing", "").replace("...", "").trim();
          if (txt && !txt.includes("Loading")) this.activeTopicTitle = txt;
        }
      }
      if (!this.activeTopicTitle) {
        const input = document.getElementById('topic-input') || document.getElementById('search-input');
        if (input && input.value && input.value.trim()) this.activeTopicTitle = input.value.trim();
      }

      this.updateTopicBanner();
    }

    updateTopicBanner() {
      const banner = document.getElementById('chat-topic-banner');
      const text = document.getElementById('chat-topic-banner-text');
      if (banner && text) {
        if (this.activeTopicTitle) {
          banner.style.display = 'flex';
          text.textContent = `Active Topic: ${this.activeTopicTitle}`;
        } else {
          banner.style.display = 'none';
        }
      }
    }

    toggleChat() {
      this.isOpen ? this.closeChat() : this.openChat();
    }

    openChat() {
      this.detectActiveTopic();
      this.isOpen = true;
      this.isMinimized = false;
      const win = document.getElementById('chatbot-window');
      win.classList.remove('minimized');
      win.classList.add('active');

      const input = document.getElementById('chatbot-input');
      setTimeout(() => input.focus(), 150);
      this.scrollToBottom();
    }

    closeChat() {
      this.isOpen = false;
      const win = document.getElementById('chatbot-window');
      win.classList.remove('active', 'minimized');
    }

    minimizeChat() {
      const win = document.getElementById('chatbot-window');
      this.isMinimized = !this.isMinimized;
      if (this.isMinimized) win.classList.add('minimized');
      else win.classList.remove('minimized');
    }

    clearChat() {
      this.chatHistory = [];
      const body = document.getElementById('chatbot-body');
      body.innerHTML = '';
      this.appendMessage('ai', 'Chat history cleared. How else can I assist you with PulseShift?');
    }

    async handleSendMessage(userText) {
      this.detectActiveTopic();
      this.isProcessing = true;

      this.appendMessage('user', userText);
      const typingId = this.showTypingIndicator();
      this.scrollToBottom();

      try {
        const payload = {
          message: userText,
          topic_title: this.activeTopicTitle || null,
          topic_id: this.activeTopicId || null,
          context: window.currentTopicData || null
        };

        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        this.removeTypingIndicator(typingId);

        if (!res.ok) throw new Error(`API error ${res.status}`);

        const data = await res.json();
        this.appendMessage('ai', data.reply || "No response received.");
      } catch (err) {
        this.removeTypingIndicator(typingId);
        this.appendMessage('ai', "⚠️ Could not connect to Gemini API. Please check server logs and connection.");
      } finally {
        this.isProcessing = false;
        this.scrollToBottom();
      }
    }

    appendMessage(sender, text) {
      const body = document.getElementById('chatbot-body');
      const row = document.createElement('div');
      row.className = `chat-row ${sender === 'user' ? 'user-row' : 'ai-row'}`;

      const avatarContent = sender === 'user'
        ? '<i class="fa-solid fa-user"></i>'
        : '<img src="/static/assets/pulseshift_ai_avatar.png" alt="AI">';
      const formattedHtml = this.formatMarkdown(text);

      row.innerHTML = `
        <div class="chat-avatar-mini">${avatarContent}</div>
        <div class="chat-bubble">${formattedHtml}</div>
      `;

      body.appendChild(row);
      this.scrollToBottom();
    }

    formatMarkdown(txt) {
      if (!txt) return '';
      let html = txt
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

      html = html.replace(/### (.*?)\n/g, '<h3>$1</h3>');
      html = html.replace(/## (.*?)\n/g, '<h4>$1</h4>');
      html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
      html = html.replace(/`(.*?)`/g, '<code>$1</code>');
      html = html.replace(/- (.*?)\n/g, '<li>$1</li>');
      html = html.replace(/\n\n/g, '<br><br>');
      html = html.replace(/\n/g, '<br>');

      return html;
    }

    showTypingIndicator() {
      const body = document.getElementById('chatbot-body');
      const id = 'typing-' + Date.now();
      const row = document.createElement('div');
      row.id = id;
      row.className = 'chat-row ai-row';
      row.innerHTML = `
        <div class="chat-avatar-mini"><img src="/static/assets/pulseshift_ai_avatar.png" alt="AI"></div>
        <div class="chat-bubble">
          <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
      `;
      body.appendChild(row);
      return id;
    }

    removeTypingIndicator(id) {
      const el = document.getElementById(id);
      if (el) el.remove();
    }

    scrollToBottom() {
      const body = document.getElementById('chatbot-body');
      if (body) body.scrollTop = body.scrollHeight;
    }
  }

  window.addEventListener('DOMContentLoaded', () => {
    window.pulseShiftChatbot = new PulseShiftGeminiChatbot();
  });
})();
