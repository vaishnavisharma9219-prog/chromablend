/**
 * CHROMA BLEND — Daily Planner Controller
 * Manages Morning, Afternoon, and Evening agenda items.
 */

const PlannerManager = {
  selectedDate: new Date().toISOString().split('T')[0],

  init() {
    this.updateDateDisplay();
    this.loadEntries();
    this.bindEvents();
  },

  updateDateDisplay() {
    const headerDate = document.getElementById('header-current-date');
    if (headerDate) {
      const options = { weekday: 'long', month: 'long', day: 'numeric' };
      const today = new Date();
      headerDate.textContent = today.toLocaleDateString('en-US', options);
    }
  },

  async loadEntries() {
    try {
      const res = await API.get('/planner', { date: this.selectedDate });
      if (res && res.data) {
        this.renderSection('morning', res.data.morning || []);
        this.renderSection('afternoon', res.data.afternoon || []);
        this.renderSection('evening', res.data.evening || []);
      }
    } catch (err) {
      console.error('Failed to load planner entries:', err);
    }
  },

  renderSection(sectionName, items) {
    const container = document.getElementById(`planner-${sectionName}-list`);
    if (!container) return;

    container.innerHTML = '';
    if (items.length === 0) {
      container.innerHTML = `<li class="empty-state" style="padding: 0.85rem 0.5rem; font-size: 0.85rem;">Nothing planned yet.</li>`;
      return;
    }

    items.forEach(item => {
      const li = document.createElement('li');
      li.className = 'planner-item';
      li.innerHTML = `
        <span>${escapeHtml(item.content)}</span>
        <button class="planner-item-delete" title="Remove" onclick="PlannerManager.deleteEntry(${item.id})">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      `;
      container.appendChild(li);
    });
  },

  bindEvents() {
    ['morning', 'afternoon', 'evening'].forEach(sec => {
      const form = document.getElementById(`planner-${sec}-form`);
      const input = document.getElementById(`planner-${sec}-input`);

      if (form && input) {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const content = input.value.trim();
          if (!content) return;

          try {
            await API.post('/planner', {
              date: this.selectedDate,
              section: sec,
              content
            });
            input.value = '';
            this.loadEntries();
          } catch (err) {
            showToast(err.message || 'Could not add entry', 'error');
          }
        });
      }
    });
  },

  async deleteEntry(id) {
    try {
      await API.delete(`/planner/${id}`);
      this.loadEntries();
    } catch (err) {
      showToast('Could not delete planner item', 'error');
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('planner-morning-list')) {
    PlannerManager.init();
  }
});
