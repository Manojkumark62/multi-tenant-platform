from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from services import booking_service

router = APIRouter(prefix="/bookings", tags=["V1 - Bookings"])

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingCreate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return booking_service.create_booking(db, current_tenant.id, current_user.id, data)

@router.get("/{booking_id}", response_model=BookingResponse, status_code=status.HTTP_200_OK)
def get_booking(booking_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return booking_service.get_booking(db, current_tenant.id, booking_id)

@router.get("/", response_model=list[BookingResponse], status_code=status.HTTP_200_OK)
def list_bookings(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return booking_service.list_bookings(db, current_tenant.id, current_user.id, offset, page_size)

@router.patch("/{booking_id}", response_model=BookingResponse, status_code=status.HTTP_200_OK)
def update_booking(booking_id: int, data: BookingUpdate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return booking_service.update_booking(db, current_tenant.id, booking_id, data)

@router.post("/{booking_id}/cancel", response_model=BookingResponse, status_code=status.HTTP_200_OK)
def cancel_booking(booking_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return booking_service.cancel_booking(db, current_tenant.id, booking_id)