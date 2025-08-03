from ..config.database import db, generate_uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(UUID(as_uuid=True), db.ForeignKey('jobs.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    reminder_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.id} for Job {self.job_id}>' 