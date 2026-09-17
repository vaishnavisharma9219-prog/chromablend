/**
 * CHROMA BLEND — AI Safety Planner Controller
 * Real Gemini-powered safety planning with situational choices and saved records.
 */

const SafetyPlanner = {
  selectedSituation: "I'm going somewhere",

  init() {
    this.bindEvents();
    this.loadSavedPlans();
  },

  bindEvents() {
    // Situation chip selection
    const chips = document.querySelectorAll('.situation-chip');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('selected'));
        chip.classList.add('selected');
        this.selectedSituation = chip.dataset.situation;
      });
    });

    // Plan form submission
    const form = document.getElementById('ai-planner-form');
    const submitBtn = document.getElementById('generate-plan-btn');
    const outputBox = document.getElementById('ai-plan-output');

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const details = document.getElementById('plan-details-input').value.trim();

        submitBtn.disabled = true;
        submitBtn.innerHTML = `
          <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
            <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
            <path d="M12 2a10 10 0 0 1 10 10"></path>
          </svg>
          Preparing your plan...
        `;

        outputBox.innerHTML = '<span style="color: var(--text-muted); font-style: italic;">Consulting safety planner...</span>';

        try {
          const res = await API.post('/safety/plan', {
            situation: this.selectedSituation,
            input_details: details
          });

          if (res && res.data) {
            outputBox.textContent = res.data.generated_plan;
            showToast('Personalized safety plan created and saved.', 'success');
            this.loadSavedPlans();
          }
        } catch (err) {
          outputBox.innerHTML = `
            <div style="color: var(--status-danger); padding: 0.5rem 0;">
              <strong>Unable to generate plan:</strong><br/>
              ${escapeHtml(err.message || 'The AI service could not be reached.')}
            </div>
          `;
          showToast(err.message || 'Safety planner error', 'error');
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Generate Safety Plan';
        }
      });
    }
  },

  async loadSavedPlans() {
    const listContainer = document.getElementById('saved-plans-container');
    if (!listContainer) return;

    try {
      const res = await API.get('/safety/plans');
      if (res && res.data) {
        listContainer.innerHTML = '';
        if (res.data.length === 0) {
          listContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">No previously saved plans.</p>';
          return;
        }

        res.data.forEach(plan => {
          const dateStr = new Date(plan.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          });

          const item = document.createElement('div');
          item.className = 'saved-plan-item';
          item.innerHTML = `
            <div class="saved-plan-header">
              <div>
                <strong>${escapeHtml(plan.situation)}</strong>
                <span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 0.5rem;">${dateStr}</span>
              </div>
              <button class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" onclick="SafetyPlanner.deletePlan(${plan.id})">
                Remove
              </button>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); max-height: 120px; overflow-y: auto; white-space: pre-wrap;">
              ${escapeHtml(plan.generated_plan)}
            </p>
          `;
          listContainer.appendChild(item);
        });
      }
    } catch (err) {
      console.error('Failed to load saved plans:', err);
    }
  },

  async deletePlan(id) {
    try {
      await API.delete(`/safety/plans/${id}`);
      this.loadSavedPlans();
      showToast('Plan removed.', 'info');
    } catch (err) {
      showToast('Could not remove plan', 'error');
    }
  }
};

window.SafetyPlanner = SafetyPlanner;
