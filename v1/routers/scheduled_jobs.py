from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.scheduled_job import ScheduledJobCreate, ScheduledJobResponse, ScheduledJobUpdate
from services import job_service

router = APIRouter(prefix="/scheduled-jobs", tags=["V1 - Scheduled Jobs"])

@router.post("/", response_model=ScheduledJobResponse, status_code=status.HTTP_201_CREATED)
def create_scheduled_job(data: ScheduledJobCreate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return job_service.create_scheduled_job(db, current_tenant.id, data)

@router.get("/{job_id}", response_model=ScheduledJobResponse, status_code=status.HTTP_200_OK)
def get_scheduled_job(job_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return job_service.get_scheduled_job(db, job_id, current_tenant.id)

@router.get("/", response_model=list[ScheduledJobResponse], status_code=status.HTTP_200_OK)
def list_scheduled_jobs(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return job_service.list_scheduled_jobs(db, current_tenant.id, offset, page_size)

@router.patch("/{job_id}", response_model=ScheduledJobResponse, status_code=status.HTTP_200_OK)
def update_scheduled_job(job_id: int, data: ScheduledJobUpdate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return job_service.update_scheduled_job(db, job_id, data, current_tenant.id)

@router.post("/{job_id}/cancel", response_model=ScheduledJobResponse, status_code=status.HTTP_200_OK)
def cancel_scheduled_job(job_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return job_service.cancel_scheduled_job(db, job_id, current_tenant.id)

@router.post("/{job_id}/enqueue", status_code=status.HTTP_201_CREATED)
def enqueue_scheduled_job(job_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    queue_item = job_service.enqueue_job(db, job_id, current_tenant.id)
    return {"message": "Job queued successfully", "queue_id": queue_item.id}