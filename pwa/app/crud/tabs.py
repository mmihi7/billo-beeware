from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.tables import TabCreate, Tab, TabStatus, OrderCreate, Order, OrderStatus
from ..database.models import Tab as DBTab, Order as DBOrder, OrderItem as DBOrderItem

def get_tab(db: Session, tab_id: int) -> Optional[DBTab]:
    """Get a tab by ID"""
    return db.query(DBTab).filter(DBTab.id == tab_id).first()

def get_tab_by_number(db: Session, number: str) -> Optional[DBTab]:
    """Get a tab by tab number"""
    return db.query(DBTab).filter(DBTab.number == number).first()

def get_tabs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[TabStatus] = None
) -> List[DBTab]:
    """Get a list of tabs with optional filtering by status"""
    query = db.query(DBTab)
    if status:
        query = query.filter(DBTab.status == status)
    return query.offset(skip).limit(limit).all()

def create_tab(db: Session, tab: TabCreate) -> DBTab:
    """Create a new tab"""
    db_tab = DBTab(
        number=tab.number,
        status=tab.status,
        customer_name=tab.customer_name,
        waiter_id=tab.waiter_id
    )
    db.add(db_tab)
    db.commit()
    db.refresh(db_tab)
    return db_tab

def update_tab_status(
    db: Session, 
    tab_id: int, 
    status: TabStatus,
    customer_name: Optional[str] = None
) -> Optional[DBTab]:
    """Update a tab's status and optionally customer name"""
    db_tab = get_tab(db, tab_id)
    if not db_tab:
        return None
    
    db_tab.status = status
    if customer_name is not None:
        db_tab.customer_name = customer_name
    db_tab.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_tab)
    return db_tab

def create_order(db: Session, order: OrderCreate, tab_id: int) -> DBOrder:
    """Create a new order for a tab"""
    db_order = DBOrder(
        tab_id=tab_id,
        status=order.status,
        customer_name=order.customer_name,
        special_instructions=order.special_instructions
    )
    
    db.add(db_order)
    db.flush()  # Flush to get the order ID for the items
    
    # Add order items
    for item in order.items:
        db_item = DBOrderItem(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            name=item.name,
            quantity=item.quantity,
            price=item.price,
            notes=item.notes
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int) -> Optional[DBOrder]:
    """Get an order by ID"""
    return db.query(DBOrder).filter(DBOrder.id == order_id).first()

def update_order_status(
    db: Session, 
    order_id: int, 
    status: OrderStatus
) -> Optional[DBOrder]:
    """Update an order's status"""
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    db_order.status = status
    db_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_tab_orders(
    db: Session, 
    tab_id: int,
    status: Optional[OrderStatus] = None
) -> List[DBOrder]:
    """Get all orders for a tab with optional status filter"""
    query = db.query(DBOrder).filter(DBOrder.tab_id == tab_id)
    if status:
        query = query.filter(DBOrder.status == status)
    return query.order_by(DBOrder.created_at.desc()).all()

def get_active_tab_orders(db: Session, tab_id: int) -> List[DBOrder]:
    """Get all active orders for a tab (not delivered or cancelled)"""
    return db.query(DBOrder).filter(
        DBOrder.tab_id == tab_id,
        DBOrder.status.notin_([OrderStatus.DELIVERED, OrderStatus.CANCELLED])
    ).order_by(DBOrder.created_at.desc()).all()
