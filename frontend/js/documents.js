/**
 * CHROMA BLEND — Document Vault Controller
 * Manages secure file uploads, downloads, deletions, and readiness checklists.
 */

const DocumentVault = {
  selectedCategory: 'all',

  init() {
    this.bindEvents();
    this.loadDocuments();
    this.loadChecklist();
  },

  bindEvents() {
    const uploadInput = document.getElementById('vault-file-input');
    const uploadDropZone = document.getElementById('vault-drop-zone');
    const categorySelect = document.getElementById('vault-category-select');

    if (uploadDropZone && uploadInput) {
      uploadDropZone.addEventListener('click', () => uploadInput.click());

      uploadDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadDropZone.classList.add('dragover');
      });

      uploadDropZone.addEventListener('dragleave', () => {
        uploadDropZone.classList.remove('dragover');
      });

      uploadDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadDropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
          this.uploadFile(e.dataTransfer.files[0]);
        }
      });

      uploadInput.addEventListener('change', () => {
        if (uploadInput.files.length) {
          this.uploadFile(uploadInput.files[0]);
        }
      });
    }

    // Category filter pills
    const pills = document.querySelectorAll('.vault-filter-bar .filter-tab');
    pills.forEach(pill => {
      pill.addEventListener('click', () => {
        pills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.selectedCategory = pill.dataset.category;
        this.loadDocuments();
      });
    });
  },

  async uploadFile(file) {
    const categorySelect = document.getElementById('vault-category-select');
    const category = categorySelect ? categorySelect.value : 'Other';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    showToast('Uploading document to vault...', 'info');

    try {
      await API.upload('/documents', formData);
      showToast('Document securely stored in vault.', 'success');
      // Reset input
      const input = document.getElementById('vault-file-input');
      if (input) input.value = '';
      this.loadDocuments();
    } catch (err) {
      showToast(err.message || 'Upload failed', 'error');
    }
  },

  async loadDocuments() {
    const grid = document.getElementById('vault-docs-grid');
    if (!grid) return;

    try {
      const params = {};
      if (this.selectedCategory && this.selectedCategory !== 'all') {
        params.category = this.selectedCategory;
      }

      const res = await API.get('/documents', params);
      if (res && res.data) {
        grid.innerHTML = '';
        if (res.data.length === 0) {
          grid.innerHTML = '<div class="empty-state">No documents in this category.</div>';
          return;
        }

        res.data.forEach(doc => {
          const sizeKb = Math.round(doc.file_size / 1024);
          const dateStr = new Date(doc.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          });

          const row = document.createElement('div');
          row.className = 'doc-row';
          row.innerHTML = `
            <div class="doc-info">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--accent-blue);">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
              <div>
                <div class="doc-name">${escapeHtml(doc.original_filename)}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; gap: 0.75rem; align-items: center; margin-top: 0.2rem;">
                  <span class="badge badge-charcoal">${escapeHtml(doc.category)}</span>
                  <span>${sizeKb} KB</span>
                  <span>${dateStr}</span>
                </div>
              </div>
            </div>
            <div class="doc-actions">
              <a href="/api/documents/${doc.id}/download" class="btn-secondary" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;" download>
                Download
              </a>
              <button class="btn-secondary" style="padding: 0.35rem 0.5rem; font-size: 0.8rem; color: var(--status-danger);" onclick="DocumentVault.deleteDoc(${doc.id})">
                Remove
              </button>
            </div>
          `;
          grid.appendChild(row);
        });
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  },

  async deleteDoc(id) {
    if (!confirm('Are you sure you want to remove this document from your vault?')) return;

    try {
      await API.delete(`/documents/${id}`);
      showToast('Document removed.', 'info');
      this.loadDocuments();
    } catch (err) {
      showToast('Could not remove document', 'error');
    }
  },

  async loadChecklist() {
    const container = document.getElementById('checklist-container');
    if (!container) return;

    try {
      const res = await API.get('/documents/checklist');
      if (res && res.data) {
        container.innerHTML = '';
        res.data.forEach(item => {
          const li = document.createElement('li');
          li.className = 'checklist-item';
          li.innerHTML = `
            <input type="checkbox" id="chk-${item.key}" ${item.is_checked ? 'checked' : ''} onchange="DocumentVault.toggleChecklist('${item.key}', this.checked)">
            <label for="chk-${item.key}">${escapeHtml(item.label)}</label>
          `;
          container.appendChild(li);
        });
      }
    } catch (err) {
      console.error('Failed to load checklist:', err);
    }
  },

  async toggleChecklist(itemKey, isChecked) {
    try {
      await API.post('/documents/checklist', {
        item_key: itemKey,
        is_checked: isChecked
      });
    } catch (err) {
      showToast('Could not update checklist', 'error');
    }
  }
};

window.DocumentVault = DocumentVault;
