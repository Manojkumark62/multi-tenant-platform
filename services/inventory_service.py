from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.inventory import Inventory
from models.product import Product
from v1.schemas.inventory import InventoryUpdate

def get_inventory(db: Session, tenant_id: int, product_id: int) -> Inventory:
    inventory = db.query(Inventory).filter(Inventory.tenant_id == tenant_id, Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inventory

def check_inventory_available(db: Session, tenant_id: int, product_id: int, quantity: int) -> bool:
    inventory = get_inventory(db, tenant_id, product_id)
    available_quantity = inventory.quantity - inventory.reserved_quantity
    if available_quantity < quantity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient inventory")
    return True

def reserve_inventory(db: Session, tenant_id: int, product_id: int, quantity: int, user_id: int) -> Inventory:
    inventory = get_inventory(db, tenant_id, product_id)
    available_quantity = inventory.quantity - inventory.reserved_quantity
    if available_quantity < quantity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient inventory")
    inventory.reserved_quantity += quantity
    db.flush()
    return inventory

def release_inventory(db: Session, tenant_id: int, product_id: int, quantity: int) -> Inventory:
    inventory = get_inventory(db, tenant_id, product_id)
    if inventory.reserved_quantity < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Release quantity exceeds reserved inventory")
    inventory.reserved_quantity -= quantity
    db.flush()
    return inventory

def update_inventory(db: Session, tenant_id: int, product_id: int, inventory_data: InventoryUpdate) -> Inventory:
    inventory = get_inventory(db, tenant_id, product_id)
    if inventory_data.quantity < inventory.reserved_quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity cannot be less than reserved quantity")
    inventory.quantity = inventory_data.quantity
    db.commit()
    db.refresh(inventory)
    return inventory

def list_inventory(db: Session, tenant_id: int, offset: int = 0, limit: int = 20) -> list[Inventory]:
    return db.query(Inventory).filter(Inventory.tenant_id == tenant_id).order_by(Inventory.id.desc()).offset(offset).limit(limit).all()