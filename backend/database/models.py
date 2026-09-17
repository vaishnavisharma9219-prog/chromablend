"""
Compatibility module re-exporting models from dedicated top-level database/ folder.
"""
from database.models import (
    UserModel,
    TaskModel,
    NoteModel,
    PlannerModel,
    SafetyPlanModel,
    DocumentModel,
    ContactModel,
    EmergencyModel
)

__all__ = [
    'UserModel',
    'TaskModel',
    'NoteModel',
    'PlannerModel',
    'SafetyPlanModel',
    'DocumentModel',
    'ContactModel',
    'EmergencyModel'
]
