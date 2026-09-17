from database.db import query_db, execute_db

class UserModel:
    @staticmethod
    def create(name: str, email: str, password_hash: str, passcode_hash: str):
        res = execute_db(
            """INSERT INTO users (name, email, password_hash, private_passcode_hash)
               VALUES (?, ?, ?, ?)""",
            (name, email, password_hash, passcode_hash)
        )
        return UserModel.get_by_id(res['last_id'])

    @staticmethod
    def get_by_id(user_id: int):
        return query_db(
            "SELECT id, name, email, created_at, updated_at FROM users WHERE id = ?",
            (user_id,),
            one=True
        )

    @staticmethod
    def get_auth_record(email: str):
        """Retrieve record including password & passcode hashes for verification."""
        return query_db(
            "SELECT id, name, email, password_hash, private_passcode_hash FROM users WHERE email = ?",
            (email,),
            one=True
        )

    @staticmethod
    def get_private_record(user_id: int):
        """Retrieve private passcode hash for a user."""
        return query_db(
            "SELECT id, private_passcode_hash FROM users WHERE id = ?",
            (user_id,),
            one=True
        )

    @staticmethod
    def update_passcode(user_id: int, passcode_hash: str):
        execute_db(
            "UPDATE users SET private_passcode_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (passcode_hash, user_id)
        )

class TaskModel:
    @staticmethod
    def get_all(user_id: int, date: str = None, completed: int = None):
        sql = "SELECT * FROM tasks WHERE user_id = ?"
        params = [user_id]
        if date:
            sql += " AND date = ?"
            params.append(date)
        if completed is not None:
            sql += " AND completed = ?"
            params.append(completed)
        sql += " ORDER BY completed ASC, date ASC, time ASC, id DESC"
        return query_db(sql, tuple(params))

    @staticmethod
    def get_by_id(task_id: int, user_id: int):
        return query_db(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
            one=True
        )

    @staticmethod
    def create(user_id: int, title: str, description: str = '', date: str = None, time: str = None, priority: str = 'normal'):
        res = execute_db(
            """INSERT INTO tasks (user_id, title, description, date, time, priority)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title, description, date, time, priority)
        )
        return TaskModel.get_by_id(res['last_id'], user_id)

    @staticmethod
    def update(task_id: int, user_id: int, title: str, description: str, date: str, time: str, completed: int, priority: str):
        execute_db(
            """UPDATE tasks 
               SET title = ?, description = ?, date = ?, time = ?, completed = ?, priority = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND user_id = ?""",
            (title, description, date, time, 1 if completed else 0, priority, task_id, user_id)
        )
        return TaskModel.get_by_id(task_id, user_id)

    @staticmethod
    def toggle_complete(task_id: int, user_id: int):
        task = TaskModel.get_by_id(task_id, user_id)
        if not task:
            return None
        new_state = 0 if task['completed'] else 1
        execute_db(
            """UPDATE tasks SET completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?""",
            (new_state, task_id, user_id)
        )
        return TaskModel.get_by_id(task_id, user_id)

    @staticmethod
    def delete(task_id: int, user_id: int):
        res = execute_db("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        return res['row_count'] > 0

class NoteModel:
    @staticmethod
    def get_all(user_id: int, search: str = None):
        sql = "SELECT * FROM notes WHERE user_id = ?"
        params = [user_id]
        if search:
            sql += " AND (title LIKE ? OR content LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term])
        sql += " ORDER BY updated_at DESC, id DESC"
        return query_db(sql, tuple(params))

    @staticmethod
    def get_by_id(note_id: int, user_id: int):
        return query_db(
            "SELECT * FROM notes WHERE id = ? AND user_id = ?",
            (note_id, user_id),
            one=True
        )

    @staticmethod
    def create(user_id: int, title: str, content: str = '', color_tag: str = 'charcoal'):
        res = execute_db(
            """INSERT INTO notes (user_id, title, content, color_tag)
               VALUES (?, ?, ?, ?)""",
            (user_id, title, content, color_tag)
        )
        return NoteModel.get_by_id(res['last_id'], user_id)

    @staticmethod
    def update(note_id: int, user_id: int, title: str, content: str, color_tag: str):
        execute_db(
            """UPDATE notes
               SET title = ?, content = ?, color_tag = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND user_id = ?""",
            (title, content, color_tag, note_id, user_id)
        )
        return NoteModel.get_by_id(note_id, user_id)

    @staticmethod
    def delete(note_id: int, user_id: int):
        res = execute_db("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        return res['row_count'] > 0

class PlannerModel:
    @staticmethod
    def get_for_date(user_id: int, date: str):
        return query_db(
            "SELECT * FROM planner_entries WHERE user_id = ? AND date = ? ORDER BY id ASC",
            (user_id, date)
        )

    @staticmethod
    def get_by_id(entry_id: int, user_id: int):
        return query_db(
            "SELECT * FROM planner_entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
            one=True
        )

    @staticmethod
    def create(user_id: int, date: str, section: str, content: str):
        res = execute_db(
            """INSERT INTO planner_entries (user_id, date, section, content)
               VALUES (?, ?, ?, ?)""",
            (user_id, date, section, content)
        )
        return PlannerModel.get_by_id(res['last_id'], user_id)

    @staticmethod
    def update(entry_id: int, user_id: int, content: str):
        execute_db(
            """UPDATE planner_entries
               SET content = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND user_id = ?""",
            (content, entry_id, user_id)
        )
        return PlannerModel.get_by_id(entry_id, user_id)

    @staticmethod
    def delete(entry_id: int, user_id: int):
        res = execute_db("DELETE FROM planner_entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
        return res['row_count'] > 0

class SafetyPlanModel:
    @staticmethod
    def get_all(user_id: int):
        return query_db(
            "SELECT * FROM safety_plans WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )

    @staticmethod
    def get_by_id(plan_id: int, user_id: int):
        return query_db(
            "SELECT * FROM safety_plans WHERE id = ? AND user_id = ?",
            (plan_id, user_id),
            one=True
        )

    @staticmethod
    def create(user_id: int, situation: str, input_details: str, generated_plan: str):
        res = execute_db(
            """INSERT INTO safety_plans (user_id, situation, input_details, generated_plan)
               VALUES (?, ?, ?, ?)""",
            (user_id, situation, input_details, generated_plan)
        )
        return SafetyPlanModel.get_by_id(res['last_id'], user_id)

    @staticmethod
    def delete(plan_id: int, user_id: int):
        res = execute_db("DELETE FROM safety_plans WHERE id = ? AND user_id = ?", (plan_id, user_id))
        return res['row_count'] > 0

class DocumentModel:
    @staticmethod
    def get_all(user_id: int, category: str = None):
        sql = "SELECT id, user_id, category, original_filename, file_size, mime_type, created_at FROM documents WHERE user_id = ?"
        params = [user_id]
        if category:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY created_at DESC"
        return query_db(sql, tuple(params))

    @staticmethod
    def get_by_id(doc_id: int, user_id: int):
        return query_db(
            "SELECT * FROM documents WHERE id = ? AND user_id = ?",
            (doc_id, user_id),
            one=True
        )

    @staticmethod
    def create(user_id: int, category: str, original_filename: str, stored_filename: str, file_path: str, file_size: int, mime_type: str):
        res = execute_db(
            """INSERT INTO documents (user_id, category, original_filename, stored_filename, file_path, file_size, mime_type)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, category, original_filename, stored_filename, file_path, file_size, mime_type)
        )
        return DocumentModel.get_by_id(res['last_id'], user_id)

    @staticmethod
    def delete(doc_id: int, user_id: int):
        res = execute_db("DELETE FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
        return res['row_count'] > 0

    @staticmethod
    def get_checklists(user_id: int):
        rows = query_db("SELECT item_key, is_checked FROM document_checklists WHERE user_id = ?", (user_id,))
        return {row['item_key']: bool(row['is_checked']) for row in rows}

    @staticmethod
    def set_checklist_item(user_id: int, item_key: str, is_checked: bool):
        execute_db(
            """INSERT INTO document_checklists (user_id, item_key, is_checked, updated_at)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(user_id, item_key) DO UPDATE SET is_checked = excluded.is_checked, updated_at = CURRENT_TIMESTAMP""",
            (user_id, item_key, 1 if is_checked else 0)
        )
        return DocumentModel.get_checklists(user_id)

class ContactModel:
    @staticmethod
    def get_all(user_id: int):
        return query_db(
            "SELECT * FROM trusted_contacts WHERE user_id = ? ORDER BY is_primary DESC, name ASC",
            (user_id,)
        )

    @staticmethod
    def get_by_id(contact_id: int, user_id: int):
        return query_db(
            "SELECT * FROM trusted_contacts WHERE id = ? AND user_id = ?",
            (contact_id, user_id),
            one=True
        )

    @staticmethod
    def create(user_id: int, name: str, phone: str, relationship: str = '', notes: str = '', is_primary: int = 0):
        if is_primary:
            execute_db("UPDATE trusted_contacts SET is_primary = 0 WHERE user_id = ?", (user_id,))
        res = execute_db(
            """INSERT INTO trusted_contacts (user_id, name, phone, relationship, notes, is_primary)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, name, phone, relationship, notes, 1 if is_primary else 0)
        )
        return ContactModel.get_by_id(res['last_id'], user_id)

    @staticmethod
    def update(contact_id: int, user_id: int, name: str, phone: str, relationship: str, notes: str, is_primary: int):
        if is_primary:
            execute_db("UPDATE trusted_contacts SET is_primary = 0 WHERE user_id = ? AND id != ?", (user_id, contact_id))
        execute_db(
            """UPDATE trusted_contacts
               SET name = ?, phone = ?, relationship = ?, notes = ?, is_primary = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND user_id = ?""",
            (name, phone, relationship, notes, 1 if is_primary else 0, contact_id, user_id)
        )
        return ContactModel.get_by_id(contact_id, user_id)

    @staticmethod
    def delete(contact_id: int, user_id: int):
        res = execute_db("DELETE FROM trusted_contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
        return res['row_count'] > 0

class EmergencyModel:
    @staticmethod
    def create(user_id: int, event_type: str = 'SOS_TRIGGER', status: str = 'LOGGED', notes: str = ''):
        res = execute_db(
            """INSERT INTO emergency_events (user_id, event_type, status, notes)
               VALUES (?, ?, ?, ?)""",
            (user_id, event_type, status, notes)
        )
        return query_db(
            "SELECT * FROM emergency_events WHERE id = ? AND user_id = ?",
            (res['last_id'], user_id),
            one=True
        )

    @staticmethod
    def get_history(user_id: int):
        return query_db(
            "SELECT * FROM emergency_events WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
