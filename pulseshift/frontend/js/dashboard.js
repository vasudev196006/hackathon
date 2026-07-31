/* =========================================================
   Consensus Entropy Mapper - Dashboard Logic & Data Fetching
   ========================================================= */

const API_BASE = window.location.origin.includes("netlify")
  ? "https://pulseshift-ilve.onrender.com"
  : window.location.origin;

let currentTopicData = null;
let allCommentsData = [];

document.addEventListener('DOMContentLoaded', () => {
  loadTopicsList();

  const urlParams = new URLSearchParams(window.location.search);
  const topicParam = urlParams.get('topic');

  if (topicParam) {
    runAnalysis(topicParam);
  } else {
    // Default initial topic load
    runAnalysis("Electric Vehicles");
  }

  // Topic search form submit listener
  const dashSearchForm = document.getElementById('dash-search-form');
  if (dashSearchForm) {
    dashSearchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = document.getElementById('dash-topic-input');
      if (input && input.value.trim()) {
        runAnalysis(input.value.trim());
      }
    });
  }

  // Topic selector change listener
  const topicSelector = document.getElementById('topic-selector');
  if (topicSelector) {
    topicSelector.addEventListener('change', (e) => {
      const selectedId = e.target.value;
      if (selectedId) {
        fetchTopicDetailsById(selectedId);
      }
    });
  }
});

async function loadTopicsList() {
  try {
    const res = await fetch(`${API_BASE}/topics`);
    if (res.ok) {
      const topics = await res.json();
      const selector = document.getElementById('topic-selector');
      if (selector) {
        selector.innerHTML = `<option value="">Select Analyzed Topic...</option>`;
        topics.forEach(t => {
          const opt = document.createElement('option');
          opt.value = t.id;
          opt.textContent = t.title;
          selector.appendChild(opt);
        });
      }
    }
  } catch (err) {
    console.warn("Could not load topics list:", err);
  }
}

async function runAnalysis(topicTitle) {
  setLoadingState(true, topicTitle);
  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topicTitle })
    });

    if (!res.ok) {
      throw new Error(`API error ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();
    currentTopicData = data;
    renderDashboard(data);
    loadTopicsList();
  } catch (err) {
    console.error("Analysis error:", err);
    alert(`Failed to analyze topic "${topicTitle}". Please verify server logs.`);
  } finally {
    setLoadingState(false, topicTitle);
  }
}

async function fetchTopicDetailsById(topicId) {
  try {
    const res = await fetch(`${API_BASE}/topic/${topicId}`);
    if (res.ok) {
      const data = await res.json();
      currentTopicData = data;
      renderDashboard(data);
    }
  } catch (err) {
    console.error("Error fetching topic details:", err);
  }
}

function triggerNewAnalysis() {
  if (currentTopicData && currentTopicData.topic) {
    runAnalysis(currentTopicData.topic.title);
  } else {
    runAnalysis("Electric Vehicles");
  }
}

function setLoadingState(isLoading, topicTitle) {
  const displayTitle = document.getElementById('topic-display-title');
  if (displayTitle) {
    if (isLoading) {
      displayTitle.innerHTML = `<i class="fa-solid fa-spinner fa-spin" style="color: var(--accent-indigo);"></i> Analyzing "${topicTitle}"...`;
    } else {
      displayTitle.innerHTML = `<span>${topicTitle}</span>`;
    }
  }
}

function renderDashboard(data) {
  // Update Title
  const displayTitle = document.getElementById('topic-display-title');
  if (displayTitle && data.topic) {
    displayTitle.innerHTML = `<span>${data.topic.title}</span>`;
  }

  // Update KPI Metrics
  document.getElementById('kpi-videos').textContent = data.total_videos || 0;
  document.getElementById('kpi-comments').textContent = data.total_comments || 0;
  document.getElementById('kpi-support').textContent = `${data.support_pct}%`;
  document.getElementById('kpi-oppose').textContent = `${data.oppose_pct}%`;
  document.getElementById('kpi-neutral').textContent = `${data.neutral_pct}%`;
  document.getElementById('kpi-confidence').textContent = data.avg_confidence ? data.avg_confidence.toFixed(2) : "0.00";
  document.getElementById('kpi-entropy').textContent = data.entropy ? data.entropy.toFixed(2) : "0.00";
  document.getElementById('kpi-volatility').textContent = data.volatility ? data.volatility.toFixed(2) : "0.00";

  // Consensus Classification Badge
  const badge = document.getElementById('kpi-classification-badge');
  if (badge) {
    const classification = data.classification || "High Entropy Dispersal";
    badge.textContent = classification;
    badge.className = "consensus-badge " + getClassificationClass(classification);
  }

  // AI Summary Text
  const summaryText = document.getElementById('ai-summary-text');
  if (summaryText) {
    summaryText.innerHTML = data.ai_summary || "No executive summary available.";
  }

  // Update Charts
  if (window.DashboardCharts) {
    window.DashboardCharts.updateCharts(data);
  }

  // Render Comments Table
  allCommentsData = data.top_comments || [];
  renderCommentsTable(allCommentsData);

  // Render NewsAPI Articles
  renderNewsArticles(data.news_articles || []);
}

function getClassificationClass(state) {
  switch(state) {
    case 'Genuine Consensus': return 'state-genuine';
    case 'Fragile Consensus': return 'state-fragile';
    case 'False Convergence': return 'state-false';
    case 'Polarized Disagreement': return 'state-polarized';
    default: return 'state-fragile';
  }
}

function renderCommentsTable(comments) {
  const tbody = document.getElementById('comments-table-body');
  if (!tbody) return;

  if (!comments || comments.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 2rem;">No comments found for this filter.</td></tr>`;
    return;
  }

  let html = '';
  comments.forEach(c => {
    const stanceClass = c.stance === 'support' ? 'tag-support' : (c.stance === 'oppose' ? 'tag-oppose' : 'tag-neutral');
    const confPct = Math.round((c.confidence || 0.8) * 100);

    html += `
      <tr>
        <td style="font-weight: 500; color: var(--text-main);">${escapeHtml(c.author || 'Anonymous')}</td>
        <td><span class="tag-stance ${stanceClass}">${c.stance}</span></td>
        <td>
          <div class="conf-bar-bg"><div class="conf-bar-fill" style="width: ${confPct}%;"></div></div>
          <span style="font-size: 0.78rem; color: var(--text-muted);">${confPct}%</span>
        </td>
        <td><span class="tag-reason">${c.reason || 'facts'}</span></td>
        <td style="color: var(--text-muted); font-size: 0.82rem;">${c.emotion || 'Neutral'}</td>
        <td style="max-width: 420px; word-break: break-word; color: var(--text-main); font-size: 0.85rem;">
          ${escapeHtml(c.text)}
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

function filterComments(filterType) {
  // Update filter pill UI active state
  const btns = document.querySelectorAll('.filter-btn');
  btns.forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');

  if (filterType === 'all') {
    renderCommentsTable(allCommentsData);
  } else {
    const filtered = allCommentsData.filter(c => c.stance === filterType);
    renderCommentsTable(filtered);
  }
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function renderNewsArticles(articles) {
  const container = document.getElementById('news-articles-container');
  const badge = document.getElementById('news-count-badge');
  if (!container) return;

  if (!articles || articles.length === 0) {
    if (badge) badge.textContent = '0 Articles Found';
    container.innerHTML = `<div style="text-align: center; color: var(--text-dim); padding: 2rem; grid-column: 1 / -1;">No related news articles found for this topic.</div>`;
    return;
  }

  if (badge) badge.textContent = `${articles.length} Coverage Articles`;

  const fallbackImages = [
    'https://images.unsplash.com/photo-1575517111478-7f6ab0973db2?w=600&q=80',  // Street protest crowd
    'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=80',  // Press microphones
    'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=600&q=80',  // University students
    'https://images.unsplash.com/photo-1569000971915-6a02b8d003b5?w=600&q=80',  // Street march rally
    'https://images.unsplash.com/photo-1495020689067-958852a7765e?w=600&q=80',  // Journalist notes
    'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=600&q=80',  // Student taking exam
    'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=600&q=80',  // Courthouse statue
    'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=600&q=80',  // Youth rally avenue
    'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=600&q=80',  // Reporter on scene
    'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&q=80',  // Laptop tech screen
    'https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=600&q=80',  // Wind turbines
    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=80'   // Stock chart
  ];

  let html = '';
  articles.forEach((art, idx) => {
    const fallbackSrc = fallbackImages[idx % fallbackImages.length];
    const imgSrc = art.urlToImage || fallbackSrc;
    const imgTag = `<img src="${escapeHtml(imgSrc)}" alt="News image" class="news-img" onerror="this.onerror=null; this.src='${fallbackSrc}';"/>`;
    const dateStr = art.publishedAt ? new Date(art.publishedAt).toLocaleDateString() : '';

    html += `
      <div class="news-card">
        <div>
          ${imgTag}
          <h4 class="news-title">${escapeHtml(art.title)}</h4>
          <p class="news-desc">${escapeHtml(art.description || '')}</p>
        </div>
        <div class="news-meta">
          <span>${escapeHtml(art.source || 'News')} &bull; ${dateStr}</span>
          ${art.url ? `<a href="${escapeHtml(art.url)}" target="_blank" class="news-link">Read <i class="fa-solid fa-arrow-up-right-from-square"></i></a>` : ''}
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

