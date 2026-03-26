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
