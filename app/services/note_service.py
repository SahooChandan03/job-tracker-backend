from ..models import Note, Job
from ..schemas import NoteCreate
from ..config.database import db
from typing import List, Optional
from uuid import UUID

class NoteService:
    @staticmethod
    def create_note(user_id: UUID, note_data: NoteCreate) -> Optional[Note]:
        """Create a new note for a job"""
        # Verify job exists and belongs to user
        job = Job.query.filter_by(id=note_data.job_id, user_id=user_id).first()
        if not job:
            return None
        
        note = Note(
            user_id=user_id,
            job_id=note_data.job_id,
            content=note_data.content,
            reminder_time=note_data.reminder_time
        )
        
        db.session.add(note)
        db.session.commit()
        db.session.refresh(note)
        
        return note
    
    @staticmethod
    def get_job_notes(job_id: UUID, user_id: UUID) -> List[Note]:
        """Get all notes for a specific job"""
        # Verify job belongs to user
        job = Job.query.filter_by(id=job_id, user_id=user_id).first()
        if not job:
            return []
        
        return Note.query.filter_by(job_id=job_id, user_id=user_id).order_by(Note.created_at.desc()).all()
    
    @staticmethod
    def get_note_by_id(note_id: UUID, user_id: UUID) -> Optional[Note]:
        """Get a specific note by ID"""
        return Note.query.filter_by(id=note_id, user_id=user_id).first()
    
    @staticmethod
    def delete_note(note_id: UUID, user_id: UUID) -> bool:
        """Delete a note"""
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return False
        
        db.session.delete(note)
        db.session.commit()
        
        return True 