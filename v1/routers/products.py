from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from services import product_service

router = APIRouter(prefix="/products", tags=["V1 - Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return product_service.create_product(db, current_tenant.id, data)

@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(product_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return product_service.get_product(db, current_tenant.id, product_id)

@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def list_products(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return product_service.list_products(db, current_tenant.id, offset, page_size)

@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(product_id: int, data: ProductUpdate, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return product_service.update_product(db, current_tenant.id, product_id, data)

@router.delete("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def deactivate_product(product_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return product_service.deactivate_product(db, current_tenant.id, product_id)