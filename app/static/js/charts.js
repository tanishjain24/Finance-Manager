/**
 * Finance Manager — Chart.js helpers
 */
window.FMCharts = {
  defaults: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { font: { family: 'Inter' }, padding: 16 } },
    },
  },

  colors: {
    primary: '#10b981',
    accent: '#3b82f6',
    income: '#22c55e',
    expense: '#ef4444',
    palette: ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#84cc16'],
  },

  doughnut(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: this.colors.palette.slice(0, data.length),
          borderWidth: 0,
          hoverOffset: 8,
        }],
      },
      options: {
        ...this.defaults,
        cutout: '65%',
        plugins: { ...this.defaults.plugins, legend: { position: 'bottom' } },
      },
    });
  },

  line(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    return new Chart(ctx, {
      type: 'line',
      data: { labels, datasets },
      options: {
        ...this.defaults,
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11 } } },
          y: { grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { font: { size: 11 } } },
        },
        elements: { line: { tension: 0.4 }, point: { radius: 3, hoverRadius: 6 } },
      },
    });
  },

  bar(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    return new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets },
      options: {
        ...this.defaults,
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11 } } },
          y: { grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { font: { size: 11 } } },
        },
        borderRadius: 8,
      },
    });
  },
};
