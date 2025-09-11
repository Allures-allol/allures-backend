# services/admin_service/routers/admin_delete.py
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from common.db.session import get_db

# БАЗОВЫЕ МОДЕЛИ (есть у всех)
from common.models.payment import Payment
from common.models.products import Product as ProductModel
from common.models.categories import Category as CategoryModel
from common.models.subscriptions import UserSubscription

# ОПЦИОНАЛЬНЫЕ (могут отсутствовать в твоём деплое) — импортируем защитно
try:
    from services.review_service.models.review import Review as ReviewModel  # type: ignore
except Exception:
    ReviewModel = None  # type: ignore

try:
    from services.review_service.models.recommendation import Recommendation as RecommendationModel  # type: ignore
except Exception:
    RecommendationModel = None  # type: ignore

try:
    from common.models.order import Order  # type: ignore
except Exception:
    Order = None  # type: ignore

try:
    from common.models.cart import Cart, CartItem  # type: ignore
except Exception:
    Cart = None  # type: ignore
    CartItem = None  # type: ignore

try:
    from common.models.wishlist import Wishlist  # type: ignore
except Exception:
    Wishlist = None  # type: ignore


router = APIRouter(prefix="/admin/delete", tags=["Admin Deletes"])


# ---------- PAYMENTS ----------
@router.delete("/payment", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    db: Session = Depends(get_db),
    id: Optional[int] = Query(None, description="PK payments.id"),
    invoice_id: Optional[str] = Query(None, description="Payment.provider_invoice_id (напр. Monobank invoiceId)"),
    provider: Optional[str] = Query(None, description="Фильтр по провайдеру, напр. 'monobank' (опц.)"),
):
    """
    Удаляет платёж:
    - передай ИЛИ `id`, ИЛИ `invoice_id` (ровно одно).
    - опционально сузить по `provider`.
    """
    if bool(id) == bool(invoice_id):
        raise HTTPException(status_code=400, detail="Pass exactly one of: id OR invoice_id")

    stmt = delete(Payment)
    if id:
        stmt = stmt.where(Payment.id == id)
    else:
        stmt = stmt.where(Payment.provider_invoice_id == invoice_id)
        if provider:
            stmt = stmt.where(Payment.provider == provider)

    res = db.execute(stmt)
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Payment not found")
    return


# ---------- REVIEWS ----------
@router.delete("/review/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_review(review_id: int, db: Session = Depends(get_db)):
    if ReviewModel is None:
        raise HTTPException(status_code=501, detail="Review model not available in this build")
    res = db.execute(delete(ReviewModel).where(ReviewModel.id == review_id))
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return


@router.delete("/reviews/by-product/{product_id}")
def delete_reviews_of_product_admin(
    product_id: int,
    user_id: Optional[int] = Query(None, description="Опционально — удалить только отзывы конкретного пользователя"),
    db: Session = Depends(get_db),
):
    if ReviewModel is None:
        raise HTTPException(status_code=501, detail="Review model not available in this build")
    q = delete(ReviewModel).where(ReviewModel.product_id == product_id)
    if user_id is not None:
        q = q.where(ReviewModel.user_id == user_id)
    res = db.execute(q)
    db.commit()
    return {"deleted": res.rowcount or 0}


# ---------- RECOMMENDATIONS ----------
@router.delete("/recommendation/{rec_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_recommendation(rec_id: int, db: Session = Depends(get_db)):
    if RecommendationModel is None:
        raise HTTPException(status_code=501, detail="Recommendation model not available in this build")
    res = db.execute(delete(RecommendationModel).where(RecommendationModel.id == rec_id))
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return


@router.delete("/recommendations/by-user/{user_id}")
def delete_recommendations_of_user(user_id: int, db: Session = Depends(get_db)):
    if RecommendationModel is None:
        raise HTTPException(status_code=501, detail="Recommendation model not available in this build")
    res = db.execute(delete(RecommendationModel).where(RecommendationModel.user_id == user_id))
    db.commit()
    return {"deleted": res.rowcount or 0}


# ---------- PRODUCTS / CATEGORIES ----------
@router.delete("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_product(product_id: int, db: Session = Depends(get_db)):
    res = db.execute(delete(ProductModel).where(ProductModel.id == product_id))
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return


@router.delete("/category/{category_id}")
def admin_delete_category(
    category_id: int,
    force: bool = Query(False, description="Если true — сначала удалит товары категории, затем категорию"),
    db: Session = Depends(get_db),
):
    if force:
        db.execute(delete(ProductModel).where(ProductModel.category_id == category_id))
    res = db.execute(delete(CategoryModel).where(CategoryModel.category_id == category_id))
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"deleted": int(res.rowcount)}


# ---------- ORDERS (если модель есть) ----------
@router.delete("/order/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_order(order_id: int, db: Session = Depends(get_db)):
    if Order is None:
        raise HTTPException(status_code=501, detail="Order model not available in this build")
    res = db.execute(delete(Order).where(Order.id == order_id))
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return


# ---------- CARTS (если модели есть) ----------
@router.delete("/cart/by-user/{user_id}")
def admin_delete_cart_by_user(user_id: int, db: Session = Depends(get_db)):
    if Cart is None:
        raise HTTPException(status_code=501, detail="Cart model not available in this build")
    # удалим все корзины юзера (и каскадно позиции)
    res = db.execute(delete(Cart).where(Cart.user_id == user_id))
    db.commit()
    return {"deleted_carts": res.rowcount or 0}


# ---------- WISHLIST (если модель есть) ----------
@router.delete("/wishlist")
def admin_delete_wishlist_item(
    user_id: int = Query(...),
    product_id: int = Query(...),
    db: Session = Depends(get_db),
):
    if Wishlist is None:
        raise HTTPException(status_code=501, detail="Wishlist model not available in this build")
    res = db.execute(delete(Wishlist).where(Wishlist.user_id == user_id, Wishlist.product_id == product_id))
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    return {"deleted": int(res.rowcount)}


# ---------- USER SUBSCRIPTIONS ----------
@router.delete("/user-subscriptions/{user_id}")
def admin_delete_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    res = db.execute(delete(UserSubscription).where(UserSubscription.user_id == user_id))
    db.commit()
    return {"deleted": res.rowcount or 0}
