/* =========================================================
   Consensus Entropy Mapper - Chart.js Integrations
   ========================================================= */

window.DashboardCharts = (function() {
  let stanceChart = null;
  let reasonChart = null;
  let entropyChart = null;
  let volatilityChart = null;

  // Chart defaults for dark glassmorphism design
  Chart.defaults.color = '#9ca3af';
  Chart.defaults.font.family = "'Poppins', sans-serif";

  function initStanceChart(supportPct, opposePct, neutralPct) {
    const ctx = document.getElementById('stanceChart');
    if (!ctx) return;

    if (stanceChart) stanceChart.destroy();

    stanceChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Support', 'Oppose', 'Neutral'],
        datasets: [{
          data: [supportPct, opposePct, neutralPct],
          backgroundColor: ['#10b981', '#f43f5e', '#6b7280'],
          borderColor: '#121826',
          borderWidth: 3,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 15,
              usePointStyle: true,
              font: { size: 12, weight: '500' }
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => ` ${context.label}: ${context.raw}%`
            }
          }
        },
        cutout: '72%'
      }
    });
  }

  function initReasonChart(reasonsBreakdown) {
    const ctx = document.getElementById('reasonChart');
    if (!ctx) return;

    if (reasonChart) reasonChart.destroy();

    const facts = reasonsBreakdown.facts || 0;
    const values = reasonsBreakdown.values || 0;
    const process = reasonsBreakdown.process || 0;

    reasonChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Facts', 'Values', 'Process'],
        datasets: [{
          label: 'Comment Count',
          data: [facts, values, process],
          backgroundColor: [
            'rgba(99, 102, 241, 0.85)',
            'rgba(139, 92, 246, 0.85)',
            'rgba(245, 158, 11, 0.85)'
          ],
          borderColor: ['#6366f1', '#8b5cf6', '#f59e0b'],
          borderWidth: 1,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { weight: '500' } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            beginAtZero: true
          }
        }
      }
    });
  }

  function initEntropyChart(snapshots) {
    const ctx = document.getElementById('entropyChart');
    if (!ctx) return;

    if (entropyChart) entropyChart.destroy();

    const labels = snapshots.map((s, idx) => `Snap #${idx + 1}`);
    const data = snapshots.map(s => s.entropy);

    entropyChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels.length ? labels : ['Snap #1'],
        datasets: [{
          label: 'Shannon Entropy H(P)',
          data: data.length ? data : [0.0],
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.12)',
          fill: true,
          tension: 0.35,
          pointRadius: 4,
          pointBackgroundColor: '#06b6d4'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            suggestedMin: 0,
            suggestedMax: 1.6
          }
        }
      }
    });
  }

  function initVolatilityChart(snapshots) {
    const ctx = document.getElementById('volatilityChart');
    if (!ctx) return;

    if (volatilityChart) volatilityChart.destroy();

    const labels = snapshots.map((s, idx) => `Snap #${idx + 1}`);
    const data = snapshots.map(s => s.volatility);

    volatilityChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels.length ? labels : ['Snap #1'],
        datasets: [{
          label: 'Volatility (Std Dev)',
          data: data.length ? data : [0.0],
          borderColor: '#f43f5e',
          backgroundColor: 'rgba(244, 63, 94, 0.12)',
          fill: true,
          tension: 0.35,
          pointRadius: 4,
          pointBackgroundColor: '#f43f5e'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            suggestedMin: 0,
            suggestedMax: 1.0
          }
        }
      }
    });
  }

  return {
    updateCharts: function(metrics) {
      initStanceChart(metrics.support_pct, metrics.oppose_pct, metrics.neutral_pct);
      initReasonChart(metrics.reasons_breakdown || {});
      initEntropyChart(metrics.latest_snapshots || []);
      initVolatilityChart(metrics.latest_snapshots || []);
    }
  };
})();
