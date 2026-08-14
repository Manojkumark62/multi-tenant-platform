from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.inventory import Inventory
from models.inventory_reservation import InventoryReservation
from models.order import Order
from v1.schemas.inventory_reservation import InventoryReservationCreate
from services.inventory_service import get_inventory
from utils.datetime import utc_now_naive

def create_reservation(db: Session, tenant_id: int, user_id: int, reservation_data: InventoryReservationCreate) -> InventoryReservation:
    inventory = get_inventory(db, tenant_id, reservation_data.inventory_id)
    available_quantity = inventory.quantity - inventory.reserved_quantity

    if available_quantity < reservation_data.quantity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient inventory")

    order = db.query(Order).filter(Order.id == reservation_data.order_id, Order.tenant_id == tenant_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found for this tenant and user")

    inventory.reserved_quantity += reservation_data.quantity
    reservation = InventoryReservation(
        inventory_id=reservation_data.inventory_id,
        order_id=reservation_data.order_id,
        quantity=reservation_data.quantity,
        expires_at=reservation_data.expires_at,
        status="reserved",
        created_at=utc_now_naive(),
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation

def get_reservation(db: Session, tenant_id: int, reservation_id: int) -> InventoryReservation:
    reservation = db.query(InventoryReservation).join(Inventory, Inventory.id == InventoryReservation.inventory_id).filter(InventoryReservation.id == reservation_id, Inventory.tenant_id == tenant_id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory reservation not found")
    return reservation

def release_reservation(db: Session, tenant_id: int, reservation_id: int) -> InventoryReservation:
    reservation = get_reservation(db, tenant_id, reservation_id)

    if reservation.status != "reserved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reservation is not reserved")

    inventory = get_inventory(db, tenant_id, reservation.inventory_id)
    if inventory.reserved_quantity < reservation.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reserved inventory quantity")

    inventory.reserved_quantity -= reservation.quantity
    reservation.status = "released"
    reservation.released_at = utc_now_naive()
    db.commit()
    db.refresh(reservation)
    return reservation

def expire_reservation(db: Session, tenant_id: int, reservation_id: int) -> InventoryReservation:
    reservation = get_reservation(db, tenant_id, reservation_id)

    if reservation.status != "reserved":
        return reservation

    if reservation.expires_at and reservation.expires_at > utc_now_naive():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reservation has not expired")

    inventory = get_inventory(db, tenant_id, reservation.inventory_id)
    inventory.reserved_quantity = max(0, inventory.reserved_quantity - reservation.quantity)
    reservation.status = "expired"
    reservation.released_at = utc_now_naive()
    db.commit()
    db.refresh(reservation)
    return reservation

def list_reservations(db: Session, tenant_id: int, user_id: int | None = None, offset: int = 0, limit: int = 20) -> list[InventoryReservation]:
    query = db.query(InventoryReservation).join(Inventory, Inventory.id == InventoryReservation.inventory_id).filter(Inventory.tenant_id == tenant_id)
    if user_id is not None:
        query = query.join(Order, Order.id == InventoryReservation.order_id).filter(Order.user_id == user_id)
    return query.order_by(InventoryReservation.id.desc()).offset(offset).limit(limit).all()