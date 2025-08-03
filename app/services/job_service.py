from ..models import Job, User
from ..schemas import JobCreate, JobUpdate
from ..config.database import db
from typing import List, Optional
from uuid import UUID

class JobService:
    @staticmethod
    def create_job(user_id: UUID, job_data: JobCreate) -> Job:
        """Create a new job for a user"""
        job = Job(
            user_id=user_id,
            company_name=job_data.company_name,
            position=job_data.position,
            status=job_data.status,
            applied_on=job_data.applied_on
        )
        
        db.session.add(job)
        db.session.commit()
        db.session.refresh(job)
        
        return job
    
    @staticmethod
    def get_user_jobs(user_id: UUID) -> List[Job]:
        """Get all jobs for a user"""
        print(f"Getting jobs for user {user_id}")
        return Job.query.filter_by(user_id=user_id).order_by(Job.created_at.desc()).all()
    
    @staticmethod
    def get_job_by_id(job_id: UUID, user_id: UUID) -> Optional[Job]:
        """Get a specific job by ID for a user"""
        return Job.query.filter_by(id=job_id, user_id=user_id).first()
    
    @staticmethod
    def update_job(job_id: UUID, user_id: UUID, job_data: JobUpdate) -> Optional[Job]:
        """Update a job"""
        job = Job.query.filter_by(id=job_id, user_id=user_id).first()
        if not job:
            return None
        
        # Update only provided fields
        if job_data.company_name is not None:
            job.company_name = job_data.company_name
        if job_data.position is not None:
            job.position = job_data.position
        if job_data.status is not None:
            job.status = job_data.status
        if job_data.applied_on is not None:
            job.applied_on = job_data.applied_on
        
        db.session.commit()
        db.session.refresh(job)
        
        return job
    
    @staticmethod
    def delete_job(job_id: UUID, user_id: UUID) -> bool:
        """Delete a job"""
        job = Job.query.filter_by(id=job_id, user_id=user_id).first()
        if not job:
            return False
        
        db.session.delete(job)
        db.session.commit()
        
        return True 