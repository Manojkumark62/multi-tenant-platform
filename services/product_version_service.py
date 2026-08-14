from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.product import Product
from models.product_version import ProductVersion
from v1.schemas.product_version import ProductVersionCreate, ProductVersionUpdate

def create_product_version(db: Session, tenant_id: int, product_id: int, version_data: ProductVersionCreate) -> ProductVersion:
    product = db.query(Product).filter(Product.id == product_id, Product.tenant_id == tenant_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing_version = db.query(ProductVersion).filter(ProductVersion.product_id == product_id, ProductVersion.version == version_data.version).first()
    if existing_version:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product version already exists")

    product_version = ProductVersion(
        product_id=product_id,
        version=version_data.version,
        price=version_data.price,
        description=version_data.description,
        is_active=version_data.is_active,
    )
    db.add(product_version)
    db.commit()
    db.refresh(product_version)
    return product_version

def get_product_version(db: Session, tenant_id: int, product_id: int, version_id: int) -> ProductVersion:
    product_version = (
        db.query(ProductVersion)
        .join(Product, Product.id == ProductVersion.product_id)
        .filter(ProductVersion.id == version_id, ProductVersion.product_id == product_id, Product.tenant_id == tenant_id)
        .first()
    )
    if not product_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product version not found")
    return product_version

def list_product_versions(db: Session, tenant_id: int, product_id: int) -> list[ProductVersion]:
    product = db.query(Product).filter(Product.id == product_id, Product.tenant_id == tenant_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return db.query(ProductVersion).filter(ProductVersion.product_id == product_id).order_by(ProductVersion.id.desc()).all()

def update_product_version(db: Session, tenant_id: int, product_id: int, version_id: int, version_data: ProductVersionUpdate) -> ProductVersion:
    product_version = get_product_version(db, tenant_id, product_id, version_id)
    update_data = version_data.model_dump(exclude_unset=True)

    if "version" in update_data and update_data["version"] != product_version.version:
        existing_version = db.query(ProductVersion).filter(ProductVersion.product_id == product_id, ProductVersion.version == update_data["version"], ProductVersion.id != version_id).first()
        if existing_version:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product version already exists")

    for field, value in update_data.items():
        setattr(product_version, field, value)

    db.commit()
    db.refresh(product_version)
    return product_version

def deactivate_product_version(db: Session, tenant_id: int, product_id: int, version_id: int) -> ProductVersion:
    product_version = get_product_version(db, tenant_id, product_id, version_id)
    product_version.is_active = False
    db.commit()
    db.refresh(product_version)
    return product_version