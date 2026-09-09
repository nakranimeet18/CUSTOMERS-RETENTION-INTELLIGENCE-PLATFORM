/**
 * Admin Panel layout, sidebar, stats loader, and modals
 */
document.addEventListener('DOMContentLoaded', () => {
  if (!Auth.requireAuth('admin')) return;

  setupAdminLayout();
});

function setupAdminLayout() {
  // Highlight active nav item based on URL
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href && currentPath.endsWith(href)) {
      item.classList.add('active');
    }
  });

  // Account dropdown toggle
  const accountBtn = document.getElementById('account-dropdown-btn');
  const accountMenu = document.getElementById('account-dropdown-menu');
  const adminNameDisplay = document.getElementById('admin-display-name');
  const adminAvatarDisplay = document.getElementById('admin-avatar-char');

  const user = Auth.getUser();
  if (user) {
    if (adminNameDisplay) adminNameDisplay.textContent = user.name || user.email || 'Admin';
    if (adminAvatarDisplay) adminAvatarDisplay.textContent = (user.name || 'A').substring(0, 1).toUpperCase();
  }

  if (accountBtn && accountMenu) {
    accountBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      accountMenu.classList.toggle('show');
    });

    document.addEventListener('click', () => {
      accountMenu.classList.remove('show');
    });
  }
}
