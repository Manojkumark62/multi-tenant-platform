from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from models.tenant import Tenant
from v2.schemas.inventory import InventoryResponse
from services import inventory_service

router = APIRouter(prefix="/inventory", tags=["V2 - Inventory"])

@router.get("/{product_id}", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
def get_inventory(product_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return inventory_service.get_inventory(db, current_tenant.id, product_id)

@router.get("/", response_model=list[InventoryResponse], status_code=status.HTTP_200_OK)
def list_inventory(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return inventory_service.list_inventory(db, current_tenant.id, offset, page_size)