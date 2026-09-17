/**
 * CHROMA BLEND — Trusted Contacts Controller
 * CRUD management and direct calling capabilities.
 */

const TrustedContacts = {
  contacts: [],

  init() {
    this.bindEvents();
    this.loadContacts();
  },

  async loadContacts() {
    const grid = document.getElementById('contacts-grid');
    if (!grid) return;

    try {
      const res = await API.get('/contacts');
      if (res && res.data) {
        this.contacts = res.data;
        this.renderContacts();
      }
    } catch (err) {
      console.error('Failed to load contacts:', err);
    }
  },

  renderContacts() {
    const grid = document.getElementById('contacts-grid');
    if (!grid) return;

    grid.innerHTML = '';
    if (this.contacts.length === 0) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          No trusted contacts added yet. Tap "Add Contact" to store emergency connections.
        </div>
      `;
      return;
    }

    this.contacts.forEach(c => {
      const card = document.createElement('div');
      card.className = `contact-card ${c.is_primary ? 'is-primary' : ''}`;
      
      const primaryBadge = c.is_primary 
        ? `<span class="badge badge-sage">Primary Contact</span>` 
        : '';

      card.innerHTML = `
        <div class="contact-top">
          <div>
            <div class="contact-name">${escapeHtml(c.name)}</div>
            <div class="contact-relationship">${escapeHtml(c.relationship || 'Trusted Contact')}</div>
          </div>
          ${primaryBadge}
        </div>

        <div class="contact-phone-row">
          <span class="contact-phone">${escapeHtml(c.phone)}</span>
          <a href="tel:${escapeHtml(c.phone)}" class="btn-primary" style="padding: 0.35rem 0.85rem; font-size: 0.8rem; background: var(--accent-sage);">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
            </svg>
            Call
          </a>
        </div>

        ${c.notes ? `<p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">${escapeHtml(c.notes)}</p>` : ''}

        <div class="contact-actions">
          <button class="btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem; color: var(--status-danger);" onclick="TrustedContacts.deleteContact(${c.id})">
            Remove
          </button>
        </div>
      `;
      grid.appendChild(card);
    });
  },

  bindEvents() {
    const addBtn = document.getElementById('add-contact-btn');
    const modal = document.getElementById('contact-modal');
    const modalClose = document.getElementById('contact-modal-close');
    const form = document.getElementById('contact-form');

    if (addBtn && modal) {
      addBtn.addEventListener('click', () => {
        modal.classList.add('active');
        document.getElementById('contact-name-input').value = '';
        document.getElementById('contact-phone-input').value = '';
        document.getElementById('contact-rel-input').value = '';
        document.getElementById('contact-notes-input').value = '';
        document.getElementById('contact-primary-chk').checked = false;
      });
    }

    if (modalClose && modal) {
      modalClose.addEventListener('click', () => modal.classList.remove('active'));
    }

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('contact-name-input').value.trim();
        const phone = document.getElementById('contact-phone-input').value.trim();
        const relationship = document.getElementById('contact-rel-input').value.trim();
        const notes = document.getElementById('contact-notes-input').value.trim();
        const isPrimary = document.getElementById('contact-primary-chk').checked;

        if (!name || !phone) return;

        try {
          await API.post('/contacts', {
            name,
            phone,
            relationship,
            notes,
            is_primary: isPrimary
          });
          modal.classList.remove('active');
          showToast('Contact saved.', 'success');
          this.loadContacts();
        } catch (err) {
          showToast(err.message || 'Could not save contact', 'error');
        }
      });
    }
  },

  async deleteContact(id) {
    if (!confirm('Remove this trusted contact?')) return;
    try {
      await API.delete(`/contacts/${id}`);
      this.loadContacts();
      showToast('Contact removed.', 'info');
    } catch (err) {
      showToast('Could not delete contact', 'error');
    }
  }
};

window.TrustedContacts = TrustedContacts;
