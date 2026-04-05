/* =========================================================
   Cabinet — core JS
   ========================================================= */

// CSRF injection for HTMX (POST/PUT/PATCH/DELETE)
document.addEventListener('htmx:configRequest', function (evt) {
    const method = evt.detail.verb.toUpperCase();
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        const token = document.cookie.match(/csrftoken=([^;]+)/);
        if (token) evt.detail.headers['X-CSRFToken'] = token[1];
    }
});

// Sync sidebar active links after every HTMX swap
function syncSidebarLinks() {
    const currentPath = window.location.pathname;
    const currentSearch = window.location.search;
    const fullUrl = currentPath + currentSearch;

    document.querySelectorAll('#cab-sidebar .cab-nav__item').forEach(link => {
        const href = link.getAttribute('href');
        if (!href) return;

        let isMatch = false;
        if (href.includes('?')) {
            isMatch = fullUrl.includes(href);
        } else if (href !== '/') {
            isMatch = currentPath === href || currentPath === href + '/';
        }

        link.classList.toggle('active', isMatch);
    });
}

document.body.addEventListener('htmx:afterSettle', syncSidebarLinks);
document.addEventListener('DOMContentLoaded', syncSidebarLinks);
window.addEventListener('popstate', syncSidebarLinks);

// Alpine components for Widgets
document.addEventListener('alpine:init', () => {
    Alpine.data('chartWidget', (config) => ({
        chart: null,
        init() {
            const ctx = this.$refs.canvas;
            if (!ctx) return;

            this.chart = new Chart(ctx, {
                type: config.type || 'line',
                data: {
                    labels: config.chart_labels || [],
                    datasets: [{
                        label: config.title,
                        data: config.chart_data || [],
                        borderColor: config.color || '#4f46e5',
                        backgroundColor: config.bg_color || 'rgba(79, 70, 229, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: { font: { size: 10 }, color: '#64748b' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 10 }, color: '#64748b' }
                        }
                    }
                }
            });
        }
    }));

    Alpine.data('donutWidget', (config) => ({
        chart: null,
        legend: [],
        init() {
            const ctx = this.$refs.canvas;
            if (!ctx) return;

            const labels = config.chart_labels || [];
            const data = config.chart_data || [];
            const colors = config.colors || ['#4f46e5', '#818cf8', '#c7d2fe', '#f1f5f9'];

            this.legend = labels.map((label, i) => ({
                label,
                value: data[i],
                color: colors[i % colors.length]
            }));

            this.chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 0,
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: { legend: { display: false } }
                }
            });
        }
    }));
});
