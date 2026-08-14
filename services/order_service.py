from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from models.product_version import ProductVersion
from v1.schemas.order import OrderCreate, OrderUpdate
from services.inventory_service import check_inventory_available, reserve_inventory

def create_order(db: Session, tenant_id: int, user_id: int, order_data: OrderCreate) -> Order:
    items = order_data.normalized_items
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must contain at least one item")

    product_ids = [item.product_id for item in items]
    products = db.query(Product).filter(Product.tenant_id == tenant_id, Product.id.in_(product_ids), Product.is_active.is_(True)).all()
    product_map = {product.id: product for product in products}

    if len(product_map) != len(set(product_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more products not found")

    order = Order(tenant_id=tenant_id, user_id=user_id, status="pending", total_amount=0)
    db.add(order)
    db.flush()

    total_amount = 0

    for item_data in items:
        product = product_map[item_data.product_id]
        version = None

        if item_data.product_version_id is not None:
            version = db.query(ProductVersion).filter(
                ProductVersion.id == item_data.product_version_id,
                ProductVersion.product_id == product.id,
                ProductVersion.is_active.is_(True),
            ).first()
        else:
            version = db.query(ProductVersion).filter(
                ProductVersion.product_id == product.id,
                ProductVersion.is_active.is_(True),
            ).order_by(ProductVersion.created_at.desc()).first()

        if not version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No active version found for product {product.id}")

        check_inventory_available(db, tenant_id, product.id, item_data.quantity)
        reserve_inventory(db, tenant_id, product.id, item_data.quantity, user_id)

        unit_price = version.price
        item_total = unit_price * item_data.quantity
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_version_id=version.id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            total_price=item_total,
        )
        db.add(order_item)
        total_amount += item_total

    order.total_amount = total_amount
    db.commit()
    db.refresh(order)
    return order

def get_order(db: Session, tenant_id: int, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id, Order.tenant_id == tenant_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

def list_orders(db: Session, tenant_id: int, offset: int = 0, limit: int = 20) -> list[Order]:
    return db.query(Order).filter(Order.tenant_id == tenant_id).order_by(Order.id.desc()).offset(offset).limit(limit).all()

def update_order(db: Session, tenant_id: int, order_id: int, order_data: OrderUpdate) -> Order:
    order = get_order(db, tenant_id, order_id)
    update_data = order_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return order

def cancel_order(db: Session, tenant_id: int, order_id: int) -> Order:
    order = get_order(db, tenant_id, order_id)

    if order.status in {"cancelled", "completed"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order cannot be cancelled")

    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order