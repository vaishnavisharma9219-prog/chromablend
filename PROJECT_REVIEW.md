# Chroma Blend — Project Review & Codebase Report

## 1. Project Overview
- **Application Name**: Chroma Blend
- **Architecture**: Separated Modular Web Application
  - **Frontend**: Vanilla HTML5, CSS3, ES6 JavaScript
  - **Backend**: Python Flask REST API
  - **Database**: SQLite3 with strict Foreign Key enforcement & Indexes
- **Design Philosophy**: Minimalist, editorial, warm, calm, human-designed daily productivity workspace disguised with a hidden, server-verified personal safety suite.

---

## 2. Folder Structure (Separated Modules)

```text
chroma-blend/
├── frontend/                  # Complete Frontend UI Layer
│   ├── index.html             # Landing & session routing
│   ├── login.html             # User login page
│   ├── register.html          # Registration with optional custom PIN
│   ├── planner.html           # Disguised daily workspace (agenda, tasks, notes)
│   ├── private.html           # Private safety suite (AI, vault, contacts, SOS)
│   ├── css/
│   │   ├── base.css           # Color tokens, typography, toasts, buttons, modals
│   │   ├── auth.css           # Login & registration styling
│   │   ├── planner.css        # 3-column workspace styling & animated checkboxes
│   │   ├── private.css        # Private suite layout, tabs, SOS hold button
│   │   └── responsive.css     # Mobile & tablet breakpoints, reduced-motion
│   └── js/
│       ├── api.js             # Centralized fetch client, cookies, toasts
│       ├── auth.js            # Auth forms & session checks
│       ├── longpress.js       # 1.7s hold trigger on logo with cancel safeguards
│       ├── planner.js         # Morning, Afternoon, Evening agenda manager
│       ├── tasks.js           # Tasks CRUD, filters (All/Active/Done), priorities
│       ├── notes.js           # Notes CRUD, live search, color tags
│       ├── private.js         # Private tab switcher, status checks, Quick Exit
│       ├── safety-planner.js  # Gemini AI safety guidance generator & saved plans
│       ├── documents.js       # Vault uploads, downloads, checklist tracker
│       ├── contacts.js        # Trusted contacts CRUD & direct tel links
│       └── sos.js             # 3-second hold SOS trigger with honest status
│
├── backend/                   # Complete Backend API Layer
│   ├── app.py                 # Flask app factory, routing, static server
│   ├── config.py              # Environment configuration & path resolution
│   ├── requirements.txt       # Dependencies (Flask, CORS, Werkzeug, Requests)
│   ├── .env.example           # Environment template
│   ├── routes/
│   │   ├── auth.py            # /api/auth (register, login, logout, me, passcode)
│   │   ├── tasks.py           # /api/tasks (CRUD & toggle)
│   │   ├── notes.py           # /api/notes (CRUD & search)
│   │   ├── planner.py         # /api/planner (Morning/Afternoon/Evening)
│   │   ├── private_access.py  # /api/private-access (verify PIN, lock, status)
│   │   ├── safety.py          # /api/safety (AI plan generation & persistence)
│   │   ├── documents.py       # /api/documents (Upload, download, delete, checklist)
│   │   ├── contacts.py        # /api/contacts (CRUD)
│   │   └── emergency.py       # /api/emergency (SOS trigger & event history)
│   ├── services/
│   │   ├── ai_service.py      # Google Gemini 2.5 Flash caller & offline fallback
│   │   ├── document_service.py# UUID file storage, MIME safety, disk removal
│   │   ├── safety_service.py  # Safety guidance prompts & persistence
│   │   └── emergency_service.py # Event logging & honest device action payloads
│   └── utils/
│       ├── security.py        # Werkzeug hashing, @login_required, @private_access_required
│       ├── validation.py      # Input validation & sanitization
│       └── responses.py       # Standardized JSON response formatting
│
├── database/                  # Dedicated Database Layer
│   ├── schema.sql             # Table schemas, foreign keys, cascades, indexes
│   ├── db.py                  # SQLite connection manager (standalone & Flask)
│   ├── models.py              # Parameterized models strictly scoped by user_id
│   └── init_db.py             # Standalone database initialization script
│
├── data/                      # File Storage Layer
│   └── uploads/               # Safe storage directory for Vault documents
│
├── tests/                     # Automated Test Suite
│   ├── test_base.py           # BaseTestCase with isolated temp DB & client
│   ├── test_auth.py           # Authentication & PIN verification tests
│   ├── test_isolation.py      # User A vs User B strict cross-isolation tests
│   ├── test_crud.py           # Tasks, notes, and agenda CRUD tests
│   ├── test_documents.py      # Vault upload, download integrity & disk cleanup tests
│   ├── test_emergency.py      # SOS trigger and contacts CRUD tests
│   ├── test_views.py          # Frontend HTML and static asset routing tests
│   └── verify_e2e.py          # 25-step live HTTP verification test suite
│
├── README.md                  # Complete technical documentation
└── .gitignore                 # Excludes local caches, DBs, and uploaded files
```

---

## 3. Verification & Test Summary
1. **Automated Unit Tests**: 18 tests passed (`Ran 18 tests in 7.167s ... OK`).
2. **Data Isolation Tests**:
   - User A registers, creates task, note, agenda, contact, document, emergency event.
   - User B registers, sees 0 records.
   - User B attempts direct tampering with User A IDs (`/api/tasks/1`, `/api/documents/1/download`) -> returned 404/403.
   - User A logs back in -> all records and file contents intact.
3. **Live 25-Step Verification**: Executed against live HTTP server on port 5005 with 100% success across all checklist items.

---

## 4. How to Run
```bash
# 1. Navigate to project
cd chroma-blend

# 2. Run backend
python backend/app.py

# 3. Access in browser
http://127.0.0.1:5000/
```
