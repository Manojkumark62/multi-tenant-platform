from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.product import Product
from v1.schemas.product import ProductCreate, ProductUpdate

def create_product(db: Session, tenant_id: int, product_data: ProductCreate) -> Product:
    existing_product = db.query(Product).filter(Product.tenant_id == tenant_id, Product.sku == product_data.sku).first()
    if existing_product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product with this SKU already exists")

    product = Product(
        tenant_id=tenant_id,
        name=product_data.name,
        sku=product_data.sku,
        description=product_data.description,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_product(db: Session, tenant_id: int, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id, Product.tenant_id == tenant_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

def get_product_by_sku(db: Session, tenant_id: int, sku: str) -> Product | None:
    return db.query(Product).filter(Product.tenant_id == tenant_id, Product.sku == sku).first()

def list_products(db: Session, tenant_id: int, offset: int = 0, limit: int = 20) -> list[Product]:
    return db.query(Product).filter(Product.tenant_id == tenant_id).order_by(Product.id.desc()).offset(offset).limit(limit).all()

def update_product(db: Session, tenant_id: int, product_id: int, product_data: ProductUpdate) -> Product:
    product = get_product(db, tenant_id, product_id)
    update_data = product_data.model_dump(exclude_unset=True)

    if "sku" in update_data and update_data["sku"] != product.sku:
        existing_product = db.query(Product).filter(Product.tenant_id == tenant_id, Product.sku == update_data["sku"], Product.id != product_id).first()
        if existing_product:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product SKU is already in use")

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

def deactivate_product(db: Session, tenant_id: int, product_id: int) -> Product:
    product = get_product(db, tenant_id, product_id)
    product.is_active = False
    db.commit()
    db.refresh(product)
    return product