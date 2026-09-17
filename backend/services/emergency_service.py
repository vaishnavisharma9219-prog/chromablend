from backend.database.models import EmergencyModel, ContactModel

def trigger_sos(user_id: int, notes: str = ''):
    """
    Log an emergency SOS event and retrieve verified contacts for immediate device actions.
    Provides honest reporting: explicitly clarifies prototype logging vs carrier dispatch.
    """
    # 1. Fetch user's registered contacts
    contacts = ContactModel.get_all(user_id)
    primary_contact = next((c for c in contacts if c.get('is_primary')), contacts[0] if contacts else None)

    # 2. Record emergency event
    notes_detail = notes.strip() or "Deliberate user SOS trigger"
    event = EmergencyModel.create(
        user_id=user_id,
        event_type="SOS_TRIGGER",
        status="RECORDED",
        notes=notes_detail
    )

    # 3. Return honest status
    return {
        "event_id": event['id'],
        "timestamp": event['created_at'],
        "status": "RECORDED",
        "message": "Emergency SOS event recorded securely. External dispatch services are not connected to this prototype.",
        "contacts_available": len(contacts),
        "primary_contact": {
            "name": primary_contact['name'],
            "phone": primary_contact['phone']
        } if primary_contact else None,
        "recommended_actions": [
            {
                "label": "Call Primary Contact" if primary_contact else "No Primary Contact Saved",
                "action": f"tel:{primary_contact['phone']}" if primary_contact else None
            },
            {
                "label": "Call Emergency Services (911 / 112)",
                "action": "tel:911"
            }
        ]
    }
