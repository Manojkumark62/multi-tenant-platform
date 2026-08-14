from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.inventory import InventoryResponse, InventoryUpdate
from services import inventory_service

router = APIRouter(prefix="/inventory", tags=["V1 - Inventory"])

@router.get("/{product_id}", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
def get_inventory(product_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return inventory_service.get_inventory(db, current_tenant.id, product_id)

@router.get("/", response_model=list[InventoryResponse], status_code=status.HTTP_200_OK)
def list_inventory(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return inventory_service.list_inventory(db, current_tenant.id, offset, page_size)

@router.patch("/{product_id}", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
def update_inventory(product_id: int, data: InventoryUpdate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return inventory_service.update_inventory(db, current_tenant.id, product_id, data)

@router.post("/{product_id}/check", status_code=status.HTTP_200_OK)
def check_inventory(product_id: int, quantity: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    inventory_service.check_inventory_available(db, current_tenant.id, product_id, quantity)
    return {"available": True}

@router.post("/{product_id}/reserve", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
def reserve_inventory(product_id: int, quantity: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return inventory_service.reserve_inventory(db, current_tenant.id, product_id, quantity, current_user.id)

@router.post("/{product_id}/release", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
def release_inventory(product_id: int, quantity: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return inventory_service.release_inventory(db, current_tenant.id, product_id, quantity)