# Chroma Blend

**Chroma Blend** is an aesthetic, editorial personal-safety web application disguised as an intuitive daily productivity planner. The default interface functions as an elegant workspace for tasks, personal notes, and daily agendas (Morning, Afternoon, Evening) with no visible indication of safety or emergency features.

Through a deliberate hidden interaction—a **1.7-second long-press on the Chroma Blend brand mark** followed by a server-verified PIN code—the user accesses a private, secure safety suite featuring an AI Safety Planner, Document Vault, Trusted Contacts, and deliberate Emergency Support.

---

## Key Features

### 1. The Normal Disguise (Daily Productivity Workspace)
- **Daily Agenda**: Organize your day across Morning, Afternoon, and Evening focal points.
- **Tasks & To-Dos**: Full CRUD task management with priority tags (Normal, High, Low), time allocation, filter tabs (All, Active, Done), and custom animated checkboxes.
- **Notes**: Notes manager with editorial color tags (charcoal, lavender, sage, peach, blue) and instant text search.
- **Aesthetic Editorial UI**: Warm ivory, charcoal, lavender, dusty blue, soft peach, and subtle sage palette with elegant typography. Zero neon, clutter, or futuristic AI gimmickry.
- **Microcopy**: Grounded human phrasing ("Good morning.", "A few things for today.", "Nothing planned yet. Enjoy the blank space :)").

### 2. The Stealth Access Mechanism
- **Discreet Long-Press**: Hold down the Chroma Blend logo/name for 1.7 seconds. Includes subtle progressive SVG ring animation and cancel safeguards (premature release or cursor drag > 8px cancels).
- **Server-Side PIN Verification**: Discrete modal requests your private verification PIN (default: `1984`, customizable during registration). PIN is hashed using `werkzeug.security` and verified by the backend.
- **Quick Exit**: An instant-return button permanently available inside the private space that locks private access and returns to the normal planner in a single click.

### 3. Private Safety Suite
- **AI Safety Planner**:
  - Scenario options: *"I'm going somewhere"*, *"I need to get home safely"*, *"I feel uncomfortable"*, *"I want to prepare in advance"*, *"Something else"*.
  - Powered by Google Gemini through the Flask backend (API keys never exposed to frontend).
  - Calm, practical, step-by-step guidance tailored to transit safety, de-escalation, and check-in schedules.
  - Generates persistent safety plans saved securely in SQLite under the user's account.
- **Document Vault**:
  - Secure file upload (PDF, PNG, JPG, WEBP, TXT, DOCX) up to 16 MB.
  - Safe storage with UUID-based filenames in protected `data/uploads/`.
  - Categorization: *Identity*, *Emergency*, *Legal*, *Medical*, *Records*, *Other*.
  - Strict ownership-verified downloads and removals.
  - Interactive **Readiness Checklist** to track essential personal documents.
- **Trusted Contacts**:
  - Manage close emergency connections with relationship tags and notes.
  - One-tap direct `tel:` call actions.
  - Designate a Primary Emergency Contact.
- **Emergency Support / SOS**:
  - Deliberate 3-second hold activation with live visual ring countdown to prevent accidental triggers.
  - Honest status reporting: Logs emergency events securely in SQLite and exposes immediate one-tap device links to Primary Contacts and 911/112 without deceptive fake claims of external carrier dispatch.

### 4. Strict Backend Data Isolation
- Every database record is associated with the authenticated user ID (`user_id`).
- All queries, updates, deletions, and file downloads are strictly verified on the backend:
  ```python
  # Direct ID tampering is rejected with 404/403
  SELECT * FROM tasks WHERE id = ? AND user_id = ?
  ```
- User A can never view, download, update, or delete User B's tasks, notes, documents, contacts, or emergency history.

---

## Architecture & Folder Structure

```text
chroma-blend/
├── backend/
│   ├── app.py                # Flask application factory, routing & static file serving
│   ├── config.py             # Environment configuration & path resolutions
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment variable template
│   │
│   ├── database/
│   │   ├── db.py             # SQLite connection management & query execution
│   │   ├── schema.sql        # Database schema with foreign keys and indexes
│   │   └── models.py         # Strictly parameterized user-scoped data models
│   │
│   ├── routes/
│   │   ├── auth.py           # Registration, login, logout, me, passcode update
│   │   ├── tasks.py          # GET, POST, PUT, PATCH, DELETE /api/tasks
│   │   ├── notes.py          # GET, POST, PUT, DELETE /api/notes
│   │   ├── planner.py        # GET, POST, PUT, DELETE /api/planner
│   │   ├── private_access.py # POST /api/private-access/verify, lock, status
│   │   ├── safety.py         # POST /api/safety/plan, GET/DELETE saved plans
│   │   ├── documents.py      # Upload, download, delete, readiness checklist
│   │   ├── contacts.py       # GET, POST, PUT, DELETE /api/contacts
│   │   └── emergency.py      # POST /api/emergency/sos, GET emergency history
│   │
│   ├── services/
│   │   ├── ai_service.py     # Gemini REST API caller with error handling
│   │   ├── document_service.py # Safe UUID storage and disk management
│   │   ├── safety_service.py # Prompt structuring and plan persistence
│   │   └── emergency_service.py # SOS logging and honest action payloads
│   │
│   └── utils/
│       ├── security.py       # Password & PIN hashing, @login_required, @private_access_required
│       ├── validation.py     # Data sanitization and input validators
│       └── responses.py      # Standardized JSON response formatting
│
├── frontend/
│   ├── index.html            # Landing / session router
│   ├── login.html            # User login
│   ├── register.html         # User registration
│   ├── planner.html          # Normal productivity planner with hidden trigger
│   ├── private.html          # Private safety dashboard
│   │
│   ├── css/
│   │   ├── base.css          # Color tokens, typography, buttons, toasts, modals
│   │   ├── auth.css          # Login and register forms
│   │   ├── planner.css       # Daily agenda, to-do lists, notes styling
│   │   ├── private.css       # Private safety suite, vault, contacts, SOS
│   │   └── responsive.css   # Breakpoints for mobile, tablet, and reduced motion
│   │
│   └── js/
│       ├── api.js            # Centralized API fetch wrapper and notifications
│       ├── auth.js           # Authentication lifecycle
│       ├── longpress.js      # 1.7s long-press detection with cancel thresholds
│       ├── planner.js        # Agenda manager (Morning, Afternoon, Evening)
│       ├── tasks.js          # Task manager with filters and toggle
│       ├── notes.js          # Notes manager with tag filters and search
│       ├── private.js        # Private space transitions and Quick Exit
│       ├── safety-planner.js # AI safety questionnaire & plan viewer
│       ├── documents.js      # Vault upload, categorization, download, checklist
│       ├── contacts.js       # Trusted contacts manager
│       └── sos.js            # 3-second hold SOS trigger with honest status
│
├── data/
│   ├── chroma_blend.db       # SQLite database (auto-created)
│   └── uploads/              # Isolated user document uploads
│
├── tests/
│   ├── test_base.py          # Test fixtures with isolated temp DB and storage
│   ├── test_auth.py          # Authentication, validation, and session tests
│   ├── test_isolation.py     # Comprehensive User A vs User B data isolation tests
│   ├── test_crud.py          # Tasks, notes, and planner CRUD tests
│   ├── test_documents.py     # Vault upload, download ownership, and deletion tests
│   ├── test_emergency.py     # SOS trigger and contacts CRUD tests
│   ├── test_views.py         # Static asset and frontend view routing tests
│   └── verify_e2e.py         # Full 25-step live HTTP verification test suite
│
├── README.md
└── .gitignore
```

---

## Technology Stack

- **Frontend**: Vanilla HTML5, CSS3, Vanilla JavaScript (ES6+). Zero heavy frameworks required.
- **Backend**: Python 3.10+, Flask, Flask-CORS, Werkzeug, Requests.
- **Database**: SQLite3 with foreign keys (`PRAGMA foreign_keys = ON;`), transactions, and indexes.
- **AI Integration**: Google Gemini API (`gemini-2.5-flash`) via backend HTTP calls.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.10 or newer
- Git

### 2. Clone or Navigate to the Repository
```bash
cd chroma-blend
```

### 3. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` in the `backend/` directory:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```ini
# Flask secret key for session cookies
SECRET_KEY=replace-with-a-random-secret-key

# Google Gemini API Key for live AI Safety Planning (Optional: Leave empty for offline mode)
GEMINI_API_KEY=your_gemini_api_key_here

# Database path
DATABASE_PATH=../data/chroma_blend.db

# Storage for vault uploads
UPLOAD_FOLDER=../data/uploads

# Server Port
PORT=5000
DEBUG=True
```

---

## Running the Application

Start the Flask server:
```bash
python backend/app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

- **Register**: Go to `/register.html` to create an account. You can optionally specify a custom 4–8 digit PIN (default is `1984`).
- **Use Planner**: Plan morning, afternoon, and evening routines, add to-dos with time/priority, and write notes.
- **Enter Private Space**:
  1. Long-press the **Chroma Blend** logo/name at the top left for **1.7 seconds**.
  2. Enter your private PIN (e.g. `1984`) in the modal.
  3. The private safety dashboard opens.
- **Quick Exit**: Click the **Quick Exit** button in the header at any time to instantly lock private mode and return to the normal planner.

---

## Running Tests

Chroma Blend includes a comprehensive automated test suite testing auth, CRUD, file uploads, emergency workflows, frontend routes, and data isolation.

### Run Unit Tests
```bash
python -m unittest discover tests
```
*Expected output: `Ran 18 tests in ... OK`*

### Run Live End-to-End Verification
Starts the server and executes the full 25-step validation script:
```bash
python tests/verify_e2e.py
```
*Expected output: `ALL 25 VERIFICATION CHECKS COMPLETED SUCCESSFULLY!`*

---

## REST API Reference

All protected endpoints require an active session cookie. Private endpoints additionally require `session['private_unlocked'] == True`.

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new user (`name`, `email`, `password`, `passcode`) |
| `POST` | `/api/auth/login` | Sign in user (`email`, `password`) |
| `POST` | `/api/auth/logout` | Clear session and sign out |
| `GET` | `/api/auth/me` | Fetch currently authenticated user |
| `PUT` | `/api/auth/passcode` | Update private access passcode |

### Tasks
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tasks` | List user's tasks (optional `?date=`, `?completed=`) |
| `POST` | `/api/tasks` | Create task (`title`, `description`, `date`, `time`, `priority`) |
| `GET` | `/api/tasks/<id>` | Fetch single task |
| `PUT` | `/api/tasks/<id>` | Update task |
| `PATCH` | `/api/tasks/<id>/toggle`| Toggle task completed state |
| `DELETE` | `/api/tasks/<id>` | Delete task |

### Notes
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/notes` | List user's notes (optional `?search=`) |
| `POST` | `/api/notes` | Create note (`title`, `content`, `color_tag`) |
| `GET` | `/api/notes/<id>` | Fetch single note |
| `PUT` | `/api/notes/<id>` | Update note |
| `DELETE` | `/api/notes/<id>` | Delete note |

### Daily Planner
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/planner` | Fetch entries organized by section (`?date=YYYY-MM-DD`) |
| `POST` | `/api/planner` | Add agenda entry (`date`, `section`, `content`) |
| `PUT` | `/api/planner/<id>` | Update entry content |
| `DELETE` | `/api/planner/<id>` | Remove agenda entry |

### Private Access & Stealth Trigger
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/private-access/verify` | Verify passcode (`passcode`) and unlock private space |
| `POST` | `/api/private-access/lock` | Quick Exit: immediately lock private space |
| `GET` | `/api/private-access/status` | Check if private access is currently verified |

### AI Safety Planner
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/safety/situations` | List available planning situations |
| `POST` | `/api/safety/plan` | Generate and save plan (`situation`, `input_details`) |
| `GET` | `/api/safety/plans` | Retrieve user's saved safety plans |
| `DELETE` | `/api/safety/plans/<id>` | Delete saved safety plan |

### Document Vault
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/documents` | List uploaded documents (optional `?category=`) |
| `POST` | `/api/documents` | Multipart upload (`file`, `category`) |
| `GET` | `/api/documents/<id>/download` | Safely download document file |
| `DELETE` | `/api/documents/<id>` | Delete document file from disk & database |
| `GET` | `/api/documents/checklist` | Get readiness checklist state |
| `POST` | `/api/documents/checklist` | Toggle checklist item (`item_key`, `is_checked`) |

### Trusted Contacts
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/contacts` | List user's trusted contacts |
| `POST` | `/api/contacts` | Add contact (`name`, `phone`, `relationship`, `notes`, `is_primary`) |
| `GET` | `/api/contacts/<id>` | Get single contact |
| `PUT` | `/api/contacts/<id>` | Update contact |
| `DELETE` | `/api/contacts/<id>` | Delete contact |

### Emergency Support / SOS
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/emergency/sos` | Trigger SOS event (`notes`) |
| `GET` | `/api/emergency/history` | List user's emergency event log |

---

## Known Limitations & Production Considerations

1. **Prototype Disclaimer**: The Emergency SOS module records events locally and prepares one-tap device actions (`tel:`) to primary contacts and emergency dispatch (911/112). It does not automatically dispatch third-party emergency services or send automated SMS without carrier integration (e.g. Twilio).
2. **File Storage**: Uploads are stored on the local filesystem (`data/uploads/`). In cloud deployments with multiple containers, replace this with an S3 or Google Cloud Storage bucket with pre-signed download URLs.
3. **Session Cookies**: In production environments over HTTPS, configure `SESSION_COOKIE_SECURE = True` in `config.py`.
4. **Offline AI Fallback**: If no `GEMINI_API_KEY` is configured in `backend/.env`, the AI Safety Planner gracefully notifies the user to provide an API key rather than returning simulated mock responses.
