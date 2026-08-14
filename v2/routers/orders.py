from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v2.schemas.order import OrderResponse
from services import order_service

router = APIRouter(prefix="/orders", tags=["V2 - Orders"])

@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def get_order(order_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.get_order(db, current_tenant.id, order_id)

@router.get("/", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
def list_orders(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return order_service.list_orders(db, current_tenant.id, offset, page_size)