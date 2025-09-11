# services/product_service/api/cart_orders.py
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from decimal import Decimal

from common.db.session import get_db
from common.models.products import Product as ProductModel
from common.models.cart import Cart, CartItem
from common.models.order import Order, OrderItem
from services.product_service.api.schemas_cart_orders import (
    CartItemIn, CartOut, CartItemOut, OrderOut, OrderItemOut
)

router = APIRouter()

def _get_user_id(x_user_id: Optional[int], fallback: Optional[int]) -> int:
    # читаем из заголовка X-User-Id, на деве можно ?user_id=
    uid = x_user_id or fallback
    if not uid:
        raise HTTPException(401, "X-User-Id header required (or ?user_id= for dev)")
    return int(uid)

def _cart_to_out(cart: Cart, db: Session) -> CartOut:
    items_out: List[CartItemOut] = []
    if cart.items:
        # подтянем названия/картинки одним запросом
        product_ids = [i.product_id for i in cart.items]
        products = (
            db.query(ProductModel.id, ProductModel.name, ProductModel.image)
              .filter(ProductModel.id.in_(product_ids))
              .all()
        )
        meta = {p.id: {"name": p.name, "image": p.image} for p in products}
        for it in cart.items:
            m = meta.get(it.product_id, {})
            items_out.append(CartItemOut(
                product_id=it.product_id,
                qty=it.qty,
                price_snapshot=Decimal(it.price_snapshot),
                name=m.get("name"),
                image=m.get("image"),
            ))
    return CartOut(
        id=cart.id,
        user_id=cart.user_id,
        status=cart.status,
        items=items_out,
        updated_at=cart.updated_at,
    )

def _order_to_out(order: Order, db: Session) -> OrderOut:
    items_out: List[OrderItemOut] = []
    if order.items:
        product_ids = [i.product_id for i in order.items]
        products = (
            db.query(ProductModel.id, ProductModel.name, ProductModel.image)
              .filter(ProductModel.id.in_(product_ids))
              .all()
        )
        meta = {p.id: {"name": p.name, "image": p.image} for p in products}
        for it in order.items:
            m = meta.get(it.product_id, {})
            items_out.append(OrderItemOut(
                product_id=it.product_id,
                qty=it.qty,
                price_snapshot=Decimal(it.price_snapshot),
                name=m.get("name"),
                image=m.get("image"),
            ))
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=Decimal(order.total_amount),
        created_at=order.created_at,
        items=items_out,
    )

# --------- CART ---------

@router.get("/cart", response_model=CartOut, summary="Текущая корзина пользователя")
def get_cart(
    db: Session = Depends(get_db),
    x_user_id: Optional[int] = Header(None, convert_underscores=False),
    user_id: Optional[int] = Query(None),
):
    uid = _get_user_id(x_user_id, user_id)
    cart = (db.query(Cart)
              .filter(Cart.user_id == uid, Cart.status == "ACTIVE")
              .first())
    if not cart:
        cart = Cart(user_id=uid, status="ACTIVE")
        db.add(cart)
        db.commit(); db.refresh(cart)
    return _cart_to_out(cart, db)

@router.post("/cart/items", response_model=CartOut, summary="Добавить товар в корзину")
def add_to_cart(
    body: CartItemIn,
    db: Session = Depends(get_db),
    x_user_id: Optional[int] = Header(None, convert_underscores=False),
    user_id: Optional[int] = Query(None),
):
    uid = _get_user_id(x_user_id, user_id)
    cart = (db.query(Cart)
              .filter(Cart.user_id == uid, Cart.status == "ACTIVE")
              .first())
    if not cart:
        cart = Cart(user_id=uid, status="ACTIVE")
        db.add(cart); db.commit(); db.refresh(cart)

    # проверим товар
    product = db.query(ProductModel).filter(ProductModel.id == body.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    # цена снапшот
    price = Decimal(product.price)

    # если уже есть — увеличим qty
    item = (db.query(CartItem)
              .filter(CartItem.cart_id == cart.id, CartItem.product_id == body.product_id)
              .first())
    if item:
        item.qty = item.qty + int(body.qty)
        # цену не меняем, это снимок момента добавления первой позиции
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=body.product_id,
            qty=int(body.qty),
            price_snapshot=price
        )
        db.add(item)

    db.commit(); db.refresh(cart)
    return _cart_to_out(cart, db)

@router.patch("/cart/items/{product_id}", response_model=CartOut, summary="Изменить количество позиции")
def change_cart_qty(
    product_id: int,
    qty: int = Query(..., gt=-1),
    db: Session = Depends(get_db),
    x_user_id: Optional[int] = Header(None, convert_underscores=False),
    user_id: Optional[int] = Query(None),
):
    uid = _get_user_id(x_user_id, user_id)
    cart = (db.query(Cart)
              .filter(Cart.user_id == uid, Cart.status == "ACTIVE")
              .first())
    if not cart:
        raise HTTPException(404, "Active cart not found")

    item = (db.query(CartItem)
              .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
              .first())
    if not item:
        raise HTTPException(404, "Item not found")

    if qty == 0:
        db.delete(item)
    else:
        item.qty = int(qty)

    db.commit(); db.refresh(cart)
    return _cart_to_out(cart, db)

@router.delete("/cart/items/{product_id}", response_model=CartOut, summary="Удалить позицию из корзины")
def remove_cart_item(
    product_id: int,
    db: Session = Depends(get_db),
    x_user_id: Optional[int] = Header(None, convert_underscores=False),
    user_id: Optional[int] = Query(None),
):
    uid = _get_user_id(x_user_id, user_id)
    cart = (db.query(Cart)
              .filter(Cart.user_id == uid, Cart.status == "ACTIVE")
              .first())
    if not cart:
        raise HTTPException(404, "Active cart not found")

    (db.query(CartItem)
       .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
       .delete(synchronize_session=False))

    db.commit(); db.refresh(cart)
    return _cart_to_out(cart, db)

# --------- CHECKOUT / ORDERS ---------

@router.post("/orders/checkout", response_model=OrderOut, summary="Создать заказ из текущей корзины")
def checkout(
    db: Session = Depends(get_db),
    x_user_id: Optional[int] = Header(None, convert_underscores=False),
    user_id: Optional[int] = Query(None),
):
    uid = _get_user_id(x_user_id, user_id)
    cart = (db.query(Cart)
              .filter(Cart.user_id == uid, Cart.status == "ACTIVE")
              .first())
    if not cart or not cart.items:
        raise HTTPException(400, "Cart is empty")

    # посчитаем сумму, проверим наличие (минимально)
    total = Decimal("0.00")
    for it in cart.items:
        total += Decimal(it.price_snapshot) * it.qty

    # создаём заказ
    order = Order(user_id=uid, cart_id=cart.id, status="CREATED", total_amount=total)
    db.add(order); db.flush()

    for it in cart.items:
        db.add(OrderItem(
            order_id=order.id,
            product_id=it.product_id,
            qty=it.qty,
            price_snapshot=it.price_snapshot
        ))
        # можно уменьшить остатки товара тут, если нужно:
        # db.query(ProductModel).filter(ProductModel.id == it.product_id)\
        #   .update({ProductModel.current_inventory: ProductModel.current_inventory - it.qty})

    # закрываем корзину
    cart.status = "CONVERTED"
    db.commit(); db.refresh(order)

    return _order_to_out(order, db)

@router.get("/orders", response_model=List[OrderOut], summary="Список заказов пользователя")
def list_orders(
    db: Session = Depends(get_db),
    x_user_id: Optional[int] = Header(None, convert_underscores=False),
    user_id: Optional[int] = Query(None),
):
    uid = _get_user_id(x_user_id, user_id)
    orders = (db.query(Order)
                .filter(Order.user_id == uid)
                .order_by(Order.id.desc())
                .all())
    return [_order_to_out(o, db) for o in orders]

@router.get("/orders/{order_id}", response_model=OrderOut, summary="Детали заказа")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    x_user_id: Optional[int] = Header(None, convert_underscores=False),
    user_id: Optional[int] = Query(None),
):
    uid = _get_user_id(x_user_id, user_id)
    order = (db.query(Order)
               .filter(Order.id == order_id, Order.user_id == uid)
               .first())
    if not order:
        raise HTTPException(404, "Order not found")
    return _order_to_out(order, db)

@router.post("/orders/{order_id}/pay", response_model=OrderOut, summary="Оплата (mock)")
def pay_order(
    order_id: int,
    db: Session = Depends(get_db),
    x_user_id: Optional[int] = Header(None, convert_underscores=False),
    user_id: Optional[int] = Query(None),
):
    uid = _get_user_id(x_user_id, user_id)
    order = (db.query(Order)
               .filter(Order.id == order_id, Order.user_id == uid)
               .first())
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "CREATED":
        raise HTTPException(400, "Order not in CREATED status")

    order.status = "PAID"
    db.commit(); db.refresh(order)
    return _order_to_out(order, db)
