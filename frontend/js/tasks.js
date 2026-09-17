/**
 * CHROMA BLEND — Tasks Controller
 * Complete CRUD and state management for user tasks.
 */

const TaskManager = {
  currentFilter: 'all', // 'all', 'active', 'completed'
  tasks: [],

  init() {
    this.bindEvents();
    this.loadTasks();
  },

  async loadTasks() {
    const listContainer = document.getElementById('tasks-list');
    if (!listContainer) return;

    try {
      const res = await API.get('/tasks');
      if (res && res.data) {
        this.tasks = res.data;
        this.renderTasks();
      }
    } catch (err) {
      console.error('Failed to load tasks:', err);
    }
  },

  renderTasks() {
    const listContainer = document.getElementById('tasks-list');
    const counterBadge = document.getElementById('tasks-count-badge');
    if (!listContainer) return;

    // Filter tasks
    let filtered = this.tasks;
    if (this.currentFilter === 'active') {
      filtered = this.tasks.filter(t => !t.completed);
    } else if (this.currentFilter === 'completed') {
      filtered = this.tasks.filter(t => t.completed);
    }

    if (counterBadge) {
      const pendingCount = this.tasks.filter(t => !t.completed).length;
      counterBadge.textContent = pendingCount;
    }

    listContainer.innerHTML = '';
    if (filtered.length === 0) {
      listContainer.innerHTML = `
        <li class="empty-state">
          ${this.currentFilter === 'completed' ? 'No completed tasks yet.' : 'Nothing planned yet. Enjoy the blank space :)'}
        </li>
      `;
      return;
    }

    filtered.forEach(task => {
      const li = document.createElement('li');
      li.className = `task-card ${task.completed ? 'completed' : ''}`;
      
      const priorityClass = task.priority === 'high' ? 'badge-peach' : (task.priority === 'low' ? 'badge-charcoal' : 'badge-lavender');
      const timeDisplay = task.time ? `<span class="task-time">${task.time}</span>` : '';

      li.innerHTML = `
        <div class="task-checkbox-custom" onclick="TaskManager.toggleTask(${task.id})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
        <div class="task-content">
          <span class="task-title">${escapeHtml(task.title)}</span>
          <div class="task-meta">
            <span class="badge ${priorityClass}">${task.priority || 'normal'}</span>
            ${timeDisplay}
          </div>
        </div>
        <button class="task-delete-btn" title="Delete Task" onclick="TaskManager.deleteTask(${task.id})">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      `;
      listContainer.appendChild(li);
    });
  },

  bindEvents() {
    // Add task form
    const form = document.getElementById('add-task-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const titleInput = document.getElementById('task-title-input');
        const prioritySelect = document.getElementById('task-priority-select');
        const timeInput = document.getElementById('task-time-input');

        const title = titleInput.value.trim();
        if (!title) return;

        const priority = prioritySelect ? prioritySelect.value : 'normal';
        const time = timeInput ? timeInput.value : '';

        try {
          await API.post('/tasks', { title, priority, time });
          titleInput.value = '';
          if (timeInput) timeInput.value = '';
          this.loadTasks();
        } catch (err) {
          showToast(err.message || 'Unable to add task', 'error');
        }
      });
    }

    // Filter tabs
    const tabs = document.querySelectorAll('.tasks-filter-tabs .filter-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.currentFilter = tab.dataset.filter;
        this.renderTasks();
      });
    });
  },

  async toggleTask(id) {
    try {
      await API.patch(`/tasks/${id}/toggle`);
      this.loadTasks();
    } catch (err) {
      showToast('Could not update task status', 'error');
    }
  },

  async deleteTask(id) {
    try {
      await API.delete(`/tasks/${id}`);
      this.loadTasks();
    } catch (err) {
      showToast('Could not delete task', 'error');
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('tasks-list')) {
    TaskManager.init();
  }
});
