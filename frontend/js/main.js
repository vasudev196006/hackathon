/* =========================================================
   Consensus Entropy Mapper - Home Page JS Script
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
  const searchForm = document.getElementById('hero-search-form');
  const topicInput = document.getElementById('topic-input');
  const searchBtn = document.getElementById('search-btn');

  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const topic = topicInput.value.trim();
      if (topic) {
        startTopicAnalysis(topic);
      }
    });
  }
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
