/**
 * Chart.js visualization helpers for Churn Analytics
 */
const ChartHelpers = {
  renderChurnDonut(canvasId, churnedCount, retainedCount) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    return new Chart(canvas.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: ['Retained Customers', 'Churned Customers'],
        datasets: [{
          data: [retainedCount, churnedCount],
          backgroundColor: ['#10b981', '#ef4444'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  },

  renderRiskBar(canvasId, highRisk, mediumRisk, lowRisk) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    return new Chart(canvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['High Risk (>65%)', 'Medium Risk (35-65%)', 'Low Risk (<35%)'],
        datasets: [{
          label: 'Customer Count',
          data: [highRisk, mediumRisk, lowRisk],
          backgroundColor: ['#e11d48', '#f59e0b', '#0284c7'],
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
          x: { grid: { display: false } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  },

  renderCityTierChart(canvasId, tierData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    return new Chart(canvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['Tier 1 Cities', 'Tier 2 Cities', 'Tier 3 Cities'],
        datasets: [
          {
            label: 'Churned',
            data: [tierData.tier1_churn || 0, tierData.tier2_churn || 0, tierData.tier3_churn || 0],
            backgroundColor: '#ef4444',
            borderRadius: 4
          },
          {
            label: 'Retained',
            data: [tierData.tier1_retained || 0, tierData.tier2_retained || 0, tierData.tier3_retained || 0],
            backgroundColor: '#10b981',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, grid: { display: false } },
          y: { stacked: true, beginAtZero: true, grid: { color: '#f1f5f9' } }
        },
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }
};

window.ChartHelpers = ChartHelpers;
