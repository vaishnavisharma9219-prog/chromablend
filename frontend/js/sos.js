/**
 * CHROMA BLEND — Emergency Support / SOS Controller
 * Deliberate 3-second hold activation, honest status reporting, and direct tel actions.
 */

const EmergencySOS = {
  HOLD_DURATION: 3000, // 3 seconds deliberate hold
  holdTimer: null,
  progressInterval: null,
  isHolding: false,

  init() {
    this.bindHoldEvents();
    this.loadHistory();
  },

  bindHoldEvents() {
    const btn = document.getElementById('sos-hold-btn');
    const circle = document.getElementById('sos-progress-circle');
    const statusBox = document.getElementById('sos-status-box');
    const circumference = 408; // 2 * PI * 65

    if (!btn || !circle) return;

    const resetHold = () => {
      clearTimeout(this.holdTimer);
      clearInterval(this.progressInterval);
      circle.style.strokeDashoffset = circumference;
      this.isHolding = false;
      this.holdTimer = null;
      this.progressInterval = null;
      btn.style.transform = 'scale(1)';
    };

    const startHold = () => {
      this.isHolding = true;
      const startTime = Date.now();
      btn.style.transform = 'scale(0.96)';

      this.progressInterval = setInterval(() => {
        if (!this.isHolding) return;
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / this.HOLD_DURATION, 1);
        const offset = circumference - (progress * circumference);
        circle.style.strokeDashoffset = offset;
      }, 30);

      this.holdTimer = setTimeout(() => {
        resetHold();
        this.triggerSOS();
      }, this.HOLD_DURATION);
    };

    // Mouse events
    btn.addEventListener('mousedown', (e) => {
      if (e.button === 0) startHold();
    });

    window.addEventListener('mouseup', () => {
      if (this.isHolding) resetHold();
    });

    // Touch events
    btn.addEventListener('touchstart', (e) => {
      e.preventDefault();
      startHold();
    });

    btn.addEventListener('touchend', () => {
      if (this.isHolding) resetHold();
    });

    btn.addEventListener('touchcancel', () => {
      if (this.isHolding) resetHold();
    });
  },

  async triggerSOS() {
    const notesInput = document.getElementById('sos-notes-input');
    const statusBox = document.getElementById('sos-status-box');
    const notes = notesInput ? notesInput.value.trim() : '';

    showToast('Activating emergency workflow...', 'info');

    try {
      const res = await API.post('/emergency/sos', { notes });
      if (res && res.data) {
        this.renderStatus(res.data);
        this.loadHistory();
      }
    } catch (err) {
      showToast(err.message || 'Failed to record SOS event', 'error');
    }
  },

  renderStatus(data) {
    const statusBox = document.getElementById('sos-status-box');
    if (!statusBox) return;

    statusBox.classList.add('active');

    const primaryAction = data.primary_contact 
      ? `<a href="tel:${escapeHtml(data.primary_contact.phone)}" class="btn-primary" style="flex: 1; padding: 0.85rem; background: var(--accent-sage);">
           <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
             <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
           </svg>
           Call ${escapeHtml(data.primary_contact.name)}
         </a>`
      : `<div style="flex: 1; font-size: 0.85rem; color: var(--text-muted); align-self: center;">No primary contact set.</div>`;

    statusBox.innerHTML = `
      <h3 style="color: var(--status-danger); display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        Emergency Event Recorded
      </h3>
      <p style="font-size: 0.9rem; color: var(--text-primary); margin-bottom: 0.5rem;">
        Timestamp: <strong>${new Date(data.timestamp).toLocaleTimeString()}</strong> (Event #${data.event_id})
      </p>

      <div class="honest-status-badge">
        <strong>Actual Status:</strong> ${escapeHtml(data.message)}
      </div>

      <div class="emergency-actions-row">
        ${primaryAction}
        <a href="tel:911" class="btn-danger" style="flex: 1; padding: 0.85rem; justify-content: center; font-weight: 600;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
          </svg>
          Call Emergency (911)
        </a>
      </div>
    `;

    // Scroll to status
    statusBox.scrollIntoView({ behavior: 'smooth' });
  },

  async loadHistory() {
    const list = document.getElementById('sos-history-list');
    if (!list) return;

    try {
      const res = await API.get('/emergency/history');
      if (res && res.data) {
        list.innerHTML = '';
        if (res.data.length === 0) {
          list.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">No previous emergency events logged.</p>';
          return;
        }

        res.data.forEach(evt => {
          const dateStr = new Date(evt.created_at).toLocaleString();
          const item = document.createElement('div');
          item.style.cssText = 'padding: 0.65rem 0.85rem; background: var(--bg-subtle); border-radius: var(--radius-sm); font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;';
          item.innerHTML = `
            <div>
              <strong>${escapeHtml(evt.event_type)}</strong> — <span style="color: var(--text-secondary);">${escapeHtml(evt.notes || 'No details')}</span>
            </div>
            <span style="color: var(--text-muted); font-size: 0.75rem;">${dateStr}</span>
          `;
          list.appendChild(item);
        });
      }
    } catch (err) {
      console.error('Failed to load SOS history:', err);
    }
  }
};

window.EmergencySOS = EmergencySOS;
