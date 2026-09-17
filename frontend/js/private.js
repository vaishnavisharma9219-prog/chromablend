/**
 * CHROMA BLEND — Private Safety Suite Controller
 * Manages tab transitions, private session verification, and Quick Exit.
 */

const PrivateSuite = {
  currentTab: 'safety-planner',

  async init() {
    // 1. Verify user is authenticated and private access is unlocked
    try {
      const statusRes = await API.get('/private-access/status');
      if (!statusRes || !statusRes.data || !statusRes.data.unlocked) {
        // Not unlocked - redirect back to normal planner
        window.location.href = '/planner.html';
        return;
      }
    } catch (err) {
      window.location.href = '/planner.html';
      return;
    }

    this.bindTabs();
    this.bindQuickExit();

    // Initialize submodules
    if (window.SafetyPlanner) SafetyPlanner.init();
    if (window.DocumentVault) DocumentVault.init();
    if (window.TrustedContacts) TrustedContacts.init();
    if (window.EmergencySOS) EmergencySOS.init();
  },

  bindTabs() {
    const tabs = document.querySelectorAll('.private-nav .nav-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const target = tab.dataset.target;
        this.switchTab(target);
      });
    });
  },

  switchTab(tabId) {
    this.currentTab = tabId;
    document.querySelectorAll('.private-panel').forEach(panel => {
      panel.classList.remove('active');
    });

    const activePanel = document.getElementById(tabId);
    if (activePanel) {
      activePanel.classList.add('active');
    }
  },

  bindQuickExit() {
    const exitButtons = document.querySelectorAll('.quick-exit-trigger');
    exitButtons.forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        try {
          // Immediately notify backend to invalidate private access flag
          await API.post('/private-access/lock');
        } catch (err) {
          console.error('Quick Exit request error:', err);
        } finally {
          // Clear any private DOM content and return to planner immediately
          document.body.innerHTML = '';
          window.location.replace('/planner.html');
        }
      });
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.private-wrapper')) {
    PrivateSuite.init();
  }
});
