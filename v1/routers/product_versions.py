from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.product import Product
from models.product_version import ProductVersion
from models.tenant import Tenant
from models.user import User
from v1.schemas.product_version import ProductVersionCreate, ProductVersionResponse, ProductVersionUpdate
from services import product_version_service

router = APIRouter(prefix="/product-versions", tags=["V1 - Product Versions"])

@router.post("/", response_model=ProductVersionResponse, status_code=status.HTTP_201_CREATED)
def create_product_version(data: ProductVersionCreate, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return product_version_service.create_product_version(db, current_tenant.id, data.product_id, data)

@router.get("/{version_id}", response_model=ProductVersionResponse, status_code=status.HTTP_200_OK)
def get_product_version_by_id(version_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    product_version = (
        db.query(ProductVersion)
        .join(Product)
        .filter(ProductVersion.id == version_id, Product.tenant_id == current_tenant.id)
        .first()
    )
    if not product_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product version not found")
    return product_version

@router.get("/product/{product_id}/{version_id}", response_model=ProductVersionResponse, status_code=status.HTTP_200_OK)
def get_product_version(product_id: int, version_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return product_version_service.get_product_version(db, current_tenant.id, product_id, version_id)

@router.get("/product/{product_id}", response_model=list[ProductVersionResponse], status_code=status.HTTP_200_OK)
def list_product_versions(product_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return product_version_service.list_product_versions(db, current_tenant.id, product_id)

@router.patch("/{version_id}", response_model=ProductVersionResponse, status_code=status.HTTP_200_OK)
def update_product_version_by_id(version_id: int, data: ProductVersionUpdate, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    product_version = (
        db.query(ProductVersion)
        .join(Product)
        .filter(ProductVersion.id == version_id, Product.tenant_id == current_tenant.id)
        .first()
    )
    if not product_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product version not found")
    return product_version_service.update_product_version(db, current_tenant.id, product_version.product_id, version_id, data)

@router.patch("/product/{product_id}/{version_id}", response_model=ProductVersionResponse, status_code=status.HTTP_200_OK)
def update_product_version(product_id: int, version_id: int, data: ProductVersionUpdate, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return product_version_service.update_product_version(db, current_tenant.id, product_id, version_id, data)

@router.delete("/{version_id}", response_model=ProductVersionResponse, status_code=status.HTTP_200_OK)
def deactivate_product_version_by_id(version_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    product_version = (
        db.query(ProductVersion)
        .join(Product)
        .filter(ProductVersion.id == version_id, Product.tenant_id == current_tenant.id)
        .first()
    )
    if not product_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product version not found")
    return product_version_service.deactivate_product_version(db, current_tenant.id, product_version.product_id, version_id)

@router.delete("/product/{product_id}/{version_id}", response_model=ProductVersionResponse, status_code=status.HTTP_200_OK)
def deactivate_product_version(product_id: int, version_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return product_version_service.deactivate_product_version(db, current_tenant.id, product_id, version_id)