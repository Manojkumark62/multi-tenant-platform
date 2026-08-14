from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.scheduled_job import ScheduledJob
from models.job_queue import JobQueue
from v1.schemas.scheduled_job import ScheduledJobCreate, ScheduledJobUpdate
from utils.datetime import utc_now_naive

def create_scheduled_job(db: Session, tenant_id: int | None, job_data: ScheduledJobCreate) -> ScheduledJob:
    job = ScheduledJob(
        tenant_id=tenant_id,
        name=job_data.name,
        job_type=job_data.job_type,
        cron_expression=job_data.cron_expression,
        payload=job_data.payload,
        is_active=job_data.is_active,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_scheduled_job(db: Session, job_id: int, tenant_id: int | None = None) -> ScheduledJob:
    query = db.query(ScheduledJob).filter(ScheduledJob.id == job_id)

    if tenant_id is not None:
        query = query.filter(ScheduledJob.tenant_id == tenant_id)

    job = query.first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled job not found")
    return job

def list_scheduled_jobs(db: Session, tenant_id: int | None = None, offset: int = 0, limit: int = 20) -> list[ScheduledJob]:
    query = db.query(ScheduledJob)

    if tenant_id is not None:
        query = query.filter(ScheduledJob.tenant_id == tenant_id)

    return query.order_by(ScheduledJob.id.desc()).offset(offset).limit(limit).all()

def update_scheduled_job(db: Session, job_id: int, job_data: ScheduledJobUpdate, tenant_id: int | None = None) -> ScheduledJob:
    job = get_scheduled_job(db, job_id, tenant_id)

    update_data = job_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job

def cancel_scheduled_job(db: Session, job_id: int, tenant_id: int | None = None) -> ScheduledJob:
    job = get_scheduled_job(db, job_id, tenant_id)

    if not job.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job cannot be cancelled")

    job.is_active = False
    job.next_run_at = None
    db.commit()
    db.refresh(job)
    return job

def enqueue_job(db: Session, scheduled_job_id: int, tenant_id: int | None = None) -> JobQueue:
    job = get_scheduled_job(db, scheduled_job_id, tenant_id)

    if not job.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive job cannot be queued")

    queue_item = JobQueue(
        scheduled_job_id=job.id,
        tenant_id=job.tenant_id,
        job_type=job.job_type,
        payload=job.payload,
        status="pending",
        attempts=0,
        max_attempts=5,
        available_at=utc_now_naive(),
    )
    db.add(queue_item)
    db.commit()
    db.refresh(queue_item)
    return queue_item

def get_next_job(db: Session) -> JobQueue | None:
    return db.query(JobQueue).filter(JobQueue.status == "pending", JobQueue.available_at <= utc_now_naive()).order_by(JobQueue.id.asc()).with_for_update(skip_locked=True).first()

def mark_job_running(db: Session, queue_id: int) -> JobQueue:
    queue_item = db.query(JobQueue).filter(JobQueue.id == queue_id).first()

    if not queue_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queued job not found")

    queue_item.status = "running"
    queue_item.attempts += 1
    db.commit()
    db.refresh(queue_item)
    return queue_item

def mark_job_completed(db: Session, queue_id: int) -> JobQueue:
    queue_item = db.query(JobQueue).filter(JobQueue.id == queue_id).first()

    if not queue_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queued job not found")

    queue_item.status = "completed"
    queue_item.completed_at = utc_now_naive()
    db.commit()
    db.refresh(queue_item)
    return queue_item

def mark_job_failed(db: Session, queue_id: int, error_message: str) -> JobQueue:
    queue_item = db.query(JobQueue).filter(JobQueue.id == queue_id).first()

    if not queue_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queued job not found")

    queue_item.status = "failed"
    queue_item.error_message = error_message
    db.commit()
    db.refresh(queue_item)
    return queue_item