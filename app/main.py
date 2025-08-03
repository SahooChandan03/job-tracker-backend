import graphene
from flask import request, jsonify
from .auth.jwt import get_current_user
from .services import JobService, NoteService
from .schemas import JobCreate, JobUpdate, NoteCreate
from uuid import UUID

# GraphQL Types
class JobType(graphene.ObjectType):
    id = graphene.String()
    user_id = graphene.String()
    company_name = graphene.String()
    position = graphene.String()
    status = graphene.String()
    applied_on = graphene.Date()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

class NoteType(graphene.ObjectType):
    id = graphene.String()
    user_id = graphene.String()
    job_id = graphene.String()
    content = graphene.String()
    reminder_time = graphene.DateTime()
    created_at = graphene.DateTime()

class UserType(graphene.ObjectType):
    id = graphene.String()
    email = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    is_active = graphene.Boolean()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

# Input Types
class JobInput(graphene.InputObjectType):
    company_name = graphene.String(required=True)
    position = graphene.String(required=True)
    status = graphene.String()
    applied_on = graphene.Date(required=True)

class JobUpdateInput(graphene.InputObjectType):
    company_name = graphene.String()
    position = graphene.String()
    status = graphene.String()
    applied_on = graphene.Date()

class NoteInput(graphene.InputObjectType):
    job_id = graphene.String(required=True)
    content = graphene.String(required=True)
    reminder_time = graphene.DateTime()

# Queries
class Query(graphene.ObjectType):
    # Job queries
    jobs = graphene.List(JobType)
    job = graphene.Field(JobType, id=graphene.String(required=True))
    
    # Note queries
    job_notes = graphene.List(NoteType, job_id=graphene.String(required=True))
    
    # User query
    me = graphene.Field(UserType)
    
    def resolve_jobs(self, info):
        user = get_current_user()
        if not user:
            return []
        
        return JobService.get_user_jobs(user.id)
    
    def resolve_job(self, info, id):
        user = get_current_user()
        if not user:
            return None
        
        return JobService.get_job_by_id(UUID(id), user.id)
    
    def resolve_job_notes(self, info, job_id):
        user = get_current_user()
        if not user:
            return []
        
        return NoteService.get_job_notes(UUID(job_id), user.id)
    
    def resolve_me(self, info):
        user = get_current_user()
        return user

# Mutations
class CreateJob(graphene.Mutation):
    class Arguments:
        job_data = JobInput(required=True)
    
    job = graphene.Field(JobType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, job_data):
        user = get_current_user()
        if not user:
            return CreateJob(success=False, message="Authentication required")
        
        try:
            # Convert GraphQL input to Pydantic schema
            job_create = JobCreate(
                company_name=job_data.company_name,
                position=job_data.position,
                status=job_data.status or 'applied',
                applied_on=job_data.applied_on
            )
            
            # Use JobService for business logic
            job = JobService.create_job(user.id, job_create)
            return CreateJob(job=job, success=True, message="Job created successfully")
        except Exception as e:
            return CreateJob(success=False, message=str(e))

class UpdateJob(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        job_data = JobUpdateInput(required=True)
    
    job = graphene.Field(JobType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id, job_data):
        user = get_current_user()
        if not user:
            return UpdateJob(success=False, message="Authentication required")
        
        try:
            # Convert GraphQL input to Pydantic schema
            job_update = JobUpdate(
                company_name=job_data.company_name,
                position=job_data.position,
                status=job_data.status,
                applied_on=job_data.applied_on
            )
            
            # Use JobService for business logic
            job = JobService.update_job(UUID(id), user.id, job_update)
            if job:
                return UpdateJob(job=job, success=True, message="Job updated successfully")
            else:
                return UpdateJob(success=False, message="Job not found")
        except Exception as e:
            return UpdateJob(success=False, message=str(e))

class DeleteJob(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        user = get_current_user()
        if not user:
            return DeleteJob(success=False, message="Authentication required")
        
        try:
            # Use JobService for business logic
            success = JobService.delete_job(UUID(id), user.id)
            if success:
                return DeleteJob(success=True, message="Job deleted successfully")
            else:
                return DeleteJob(success=False, message="Job not found")
        except Exception as e:
            return DeleteJob(success=False, message=str(e))

class CreateNote(graphene.Mutation):
    class Arguments:
        note_data = NoteInput(required=True)
    
    note = graphene.Field(NoteType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, note_data):
        user = get_current_user()
        if not user:
            return CreateNote(success=False, message="Authentication required")
        
        try:
            # Convert GraphQL input to Pydantic schema
            note_create = NoteCreate(
                job_id=UUID(note_data.job_id),
                content=note_data.content,
                reminder_time=note_data.reminder_time
            )
            
            # Use NoteService for business logic
            note = NoteService.create_note(user.id, note_create)
            if note:
                return CreateNote(note=note, success=True, message="Note created successfully")
            else:
                return CreateNote(success=False, message="Job not found")
        except Exception as e:
            return CreateNote(success=False, message=str(e))

class DeleteNote(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        user = get_current_user()
        if not user:
            return DeleteNote(success=False, message="Authentication required")
        
        try:
            # Use NoteService for business logic
            success = NoteService.delete_note(UUID(id), user.id)
            if success:
                return DeleteNote(success=True, message="Note deleted successfully")
            else:
                return DeleteNote(success=False, message="Note not found")
        except Exception as e:
            return DeleteNote(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    create_job = CreateJob.Field()
    update_job = UpdateJob.Field()
    delete_job = DeleteJob.Field()
    create_note = CreateNote.Field()
    delete_note = DeleteNote.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# GraphQL endpoint handler
def graphql_handler():
    data = request.get_json()
    query = data.get('query')
    variables = data.get('variables')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    result = schema.execute(query, variable_values=variables)
    
    if result.errors:
        return jsonify({'errors': [str(error) for error in result.errors]}), 400
    
    return jsonify({'data': result.data}) 