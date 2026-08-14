from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.inventory_reservation import InventoryReservationCreate, InventoryReservationResponse
from services import inventory_reservation_service

router = APIRouter(prefix="/inventory-reservations", tags=["V1 - Inventory Reservations"])

@router.post("/", response_model=InventoryReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(data: InventoryReservationCreate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return inventory_reservation_service.create_reservation(db, current_tenant.id, current_user.id, data)

@router.get("/{reservation_id}", response_model=InventoryReservationResponse, status_code=status.HTTP_200_OK)
def get_reservation(reservation_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return inventory_reservation_service.get_reservation(db, current_tenant.id, reservation_id)

@router.get("/", response_model=list[InventoryReservationResponse], status_code=status.HTTP_200_OK)
def list_reservations(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return inventory_reservation_service.list_reservations(db, current_tenant.id, current_user.id, offset, page_size)

@router.post("/{reservation_id}/release", response_model=InventoryReservationResponse, status_code=status.HTTP_200_OK)
def release_reservation(reservation_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return inventory_reservation_service.release_reservation(db, current_tenant.id, reservation_id)

@router.post("/{reservation_id}/expire", response_model=InventoryReservationResponse, status_code=status.HTTP_200_OK)
def expire_reservation(reservation_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return inventory_reservation_service.expire_reservation(db, current_tenant.id, reservation_id)