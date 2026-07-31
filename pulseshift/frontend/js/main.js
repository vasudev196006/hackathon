/* =========================================================
   PulseShift - Compact Landing Page & Workstation Tabs Script
   ========================================================= */

const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000"
  : "https://pulseshift.onrender.com";

document.addEventListener('DOMContentLoaded', () => {
  const searchForm = document.getElementById('hero-search-form');
  const topicInput = document.getElementById('topic-input');

  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const topic = topicInput.value.trim();
      if (topic) {
        startTopicAnalysis(topic);
      }
    });
  }

  // Load live protest news feed
  loadProtestNewsFeed();
});

function quickAnalyze(topicName) {
  const input = document.getElementById('topic-input');
  if (input) {
    input.value = topicName;
  }
  startTopicAnalysis(topicName);
}

function startTopicAnalysis(topicName) {
  const searchBtn = document.getElementById('search-btn');
  if (searchBtn) {
    searchBtn.disabled = true;
    searchBtn.innerHTML = `
      <i class="fa-solid fa-spinner fa-spin"></i>
      <span>Analyzing...</span>
    `;
  }

  // Redirect to Dashboard workstation with topic query parameter
  window.location.href = `/dashboard?topic=${encodeURIComponent(topicName)}`;
}

// Tab Switching Logic
function switchTab(tabId) {
  // Update Tab Buttons
  const buttons = document.querySelectorAll('.tab-btn');
  buttons.forEach(btn => btn.classList.remove('active'));

  const activeBtn = Array.from(buttons).find(btn => btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(tabId));
  if (activeBtn) {
    activeBtn.classList.add('active');
  }

  // Update Tab Contents
  const contents = document.querySelectorAll('.tab-content');
  contents.forEach(content => content.classList.remove('active'));

  const targetContent = document.getElementById(tabId);
  if (targetContent) {
    targetContent.classList.add('active');
  }
}

async function loadProtestNewsFeed() {
  const heroContainer = document.getElementById('protest-news-list');
  const gridContainer = document.getElementById('tab-protest-news-grid');

  try {
    const res = await fetch(`${API_BASE}/news?q=protest`);
    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const articles = await res.json();
    if (!articles || articles.length === 0) {
      if (heroContainer) heroContainer.innerHTML = `<div class="news-loading-skeleton">No recent protest news found.</div>`;
      if (gridContainer) gridContainer.innerHTML = `<div class="news-loading-skeleton">No recent protest news found.</div>`;
      return;
    }

    // Populate Hero Side Card (Top 3)
    if (heroContainer) {
      heroContainer.innerHTML = articles.slice(0, 3).map(art => {
        const timeStr = art.publishedAt ? new Date(art.publishedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Live';
        const source = art.source || 'News Desk';
        return `
          <div class="news-item-card">
            <div class="news-title">${escapeHtml(art.title)}</div>
            <div class="news-meta">
              <span class="news-source"><i class="fa-regular fa-newspaper"></i> ${escapeHtml(source)}</span>
              <span class="news-time">${timeStr}</span>
            </div>
          </div>
        `;
      }).join('');
    }

    // Populate Tab Grid (Full list)
    if (gridContainer) {
      gridContainer.innerHTML = articles.map(art => {
        const timeStr = art.publishedAt ? new Date(art.publishedAt).toLocaleDateString() : 'Live';
        const source = art.source || 'News Desk';
        return `
          <div class="glass-card news-item-card" style="padding: 1rem;">
            <div class="news-title" style="font-size: 0.9rem; margin-bottom: 0.4rem;">${escapeHtml(art.title)}</div>
            <p style="font-size: 0.775rem; color: var(--text-muted); margin-bottom: 0.6rem; line-height: 1.4;">
              ${escapeHtml(art.description || '')}
            </p>
            <div class="news-meta">
              <span class="news-source"><i class="fa-regular fa-newspaper"></i> ${escapeHtml(source)}</span>
              <span class="news-time">${timeStr}</span>
            </div>
          </div>
        `;
      }).join('');
    }

  } catch (err) {
    console.warn('Failed to load live protest news feed:', err);
    const fallbacks = [
      { title: "Global Climate Rallies Mobilize Millions Across Major Hubs", source: "Reuters", desc: "Mass civic rallies reflect stance entropy and volatile sentiment across major metropolitan hubs." },
      { title: "Policy Reform Triggers Widespread Public Debate & March", source: "AP News", desc: "Online comment analysis shows a 42% spike in sentiment variance as citizens demand structural updates." },
      { title: "Youth Movement Mobilizes Digital & Physical Protest Action", source: "BBC News", desc: "Social monitoring reveals stance polarization with opposition growing rapidly across social platforms." }
    ];

    if (heroContainer) {
      heroContainer.innerHTML = fallbacks.map(f => `
        <div class="news-item-card">
          <div class="news-title">${f.title}</div>
          <div class="news-meta">
            <span class="news-source"><i class="fa-regular fa-newspaper"></i> ${f.source}</span>
            <span class="news-time">Live</span>
          </div>
        </div>
      `).join('');
    }
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
