from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.scheduled_job import JobQueueResponse
from services import job_service

router = APIRouter(prefix="/job-queue", tags=["V1 - Job Queue"])

@router.get("/next", response_model=JobQueueResponse | None, status_code=status.HTTP_200_OK)
def get_next_job(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.get_next_job(db)

@router.post("/{queue_id}/running", response_model=JobQueueResponse, status_code=status.HTTP_200_OK)
def mark_job_running(queue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.mark_job_running(db, queue_id)

@router.post("/{queue_id}/completed", response_model=JobQueueResponse, status_code=status.HTTP_200_OK)
def mark_job_completed(queue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.mark_job_completed(db, queue_id)

@router.post("/{queue_id}/failed", response_model=JobQueueResponse, status_code=status.HTTP_200_OK)
def mark_job_failed(queue_id: int, error_message: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return job_service.mark_job_failed(db, queue_id, error_message)