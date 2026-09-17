/**
 * CHROMA BLEND — Notes Controller
 * Complete CRUD and search for user notes with editorial color tags.
 */

const NoteManager = {
  notes: [],

  init() {
    this.bindEvents();
    this.loadNotes();
  },

  async loadNotes(searchTerm = '') {
    const listContainer = document.getElementById('notes-list');
    if (!listContainer) return;

    try {
      const res = await API.get('/notes', searchTerm ? { search: searchTerm } : {});
      if (res && res.data) {
        this.notes = res.data;
        this.renderNotes();
      }
    } catch (err) {
      console.error('Failed to load notes:', err);
    }
  },

  renderNotes() {
    const listContainer = document.getElementById('notes-list');
    const countBadge = document.getElementById('notes-count-badge');
    if (!listContainer) return;

    if (countBadge) {
      countBadge.textContent = this.notes.length;
    }

    listContainer.innerHTML = '';
    if (this.notes.length === 0) {
      listContainer.innerHTML = `
        <div class="empty-state">
          No notes yet. Tap "New Note" to jot down thoughts.
        </div>
      `;
      return;
    }

    this.notes.forEach(note => {
      const card = document.createElement('div');
      const tag = note.color_tag || 'charcoal';
      card.className = `note-card note-${tag}`;

      const dateStr = note.created_at ? new Date(note.created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      }) : '';

      card.innerHTML = `
        <div class="note-header">
          <h4 class="note-title">${escapeHtml(note.title)}</h4>
          <button class="note-delete-btn" title="Delete Note" onclick="NoteManager.deleteNote(${note.id})">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
        ${note.content ? `<p class="note-body">${escapeHtml(note.content)}</p>` : ''}
        <div class="note-date">${dateStr}</div>
      `;
      listContainer.appendChild(card);
    });
  },

  bindEvents() {
    // Search bar
    const searchInput = document.getElementById('notes-search-input');
    if (searchInput) {
      let debounce = null;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
          this.loadNotes(e.target.value.trim());
        }, 200);
      });
    }

    // New Note Modal / Form
    const newNoteBtn = document.getElementById('new-note-btn');
    const noteModal = document.getElementById('note-modal');
    const noteModalClose = document.getElementById('note-modal-close');
    const noteForm = document.getElementById('note-form');

    if (newNoteBtn && noteModal) {
      newNoteBtn.addEventListener('click', () => {
        noteModal.classList.add('active');
        const titleInput = document.getElementById('note-title-input');
        if (titleInput) {
          titleInput.value = '';
          setTimeout(() => titleInput.focus(), 150);
        }
        const contentInput = document.getElementById('note-content-input');
        if (contentInput) contentInput.value = '';
      });
    }

    if (noteModalClose && noteModal) {
      noteModalClose.addEventListener('click', () => {
        noteModal.classList.remove('active');
      });
    }

    if (noteForm) {
      noteForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('note-title-input').value.trim();
        const content = document.getElementById('note-content-input').value.trim();
        const colorTag = document.querySelector('input[name="note-color"]:checked')?.value || 'charcoal';

        if (!title) return;

        try {
          await API.post('/notes', { title, content, color_tag: colorTag });
          noteModal.classList.remove('active');
          this.loadNotes();
        } catch (err) {
          showToast(err.message || 'Could not save note', 'error');
        }
      });
    }
  },

  async deleteNote(id) {
    try {
      await API.delete(`/notes/${id}`);
      this.loadNotes();
    } catch (err) {
      showToast('Could not delete note', 'error');
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('notes-list')) {
    NoteManager.init();
  }
});
