#sales_service/api/controller.py
import os
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from http import HTTPStatus as HttpStatus

from common.models.sales import Sales
from common.custom_exceptions import (
    ProductNotFoundException,
    ProductOutofStockException,
    ProductInventoryUpdateException,
    NoSalesDataFoundException,
    InsufficientInventoryException,
)

# Получение деталей продукта по ID
def get_product_details_by_id(product_id: int):
    base_path = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8000")
    url = f"{base_path}/products/get_product/?product_id={product_id}"
    print("Запрос к продукту:", url)
    return requests.get(url=url)


# Обновление инвентаря продукта
def decrement_product_inventory(new_quantity: int, product_id: int):
    base_path = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8000")
    url = f"{base_path}/products/update/?product_id={product_id}"
    return requests.put(url=url, json={"current_inventory": new_quantity})

# Получение всех категорий для сопоставления ID -> name
def get_all_categories():
    base_path = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8000")
    url = f"{base_path}/categories/"
    try:
        resp = requests.get(url)
        if resp.status_code == HttpStatus.OK:
            return {c["category_id"]: c["name"] for c in resp.json()}
    except Exception as e:
        print(" Ошибка при получении категорий:", e)
    return {}

# Транзакция создания продажи
def create_product_sale_transaction(sale_data: dict, db: Session):
    try:
        db_sale = Sales(
            product_id=sale_data["product_id"],
            user_id=sale_data["user_id"],
            category_id=sale_data["category_id"],
            units_sold=sale_data["units_sold"]
        )

        print("Полученные данные:", vars(db_sale))

        product_response = get_product_details_by_id(db_sale.product_id)
        if product_response.status_code != HttpStatus.OK:
            raise ProductNotFoundException("Продукт не найден")

        product_data = product_response.json()
        current_inventory = product_data.get("current_inventory", 0)

        if current_inventory >= db_sale.units_sold:
            new_inventory = current_inventory - db_sale.units_sold
            inventory_update = decrement_product_inventory(new_inventory, db_sale.product_id)

            if inventory_update.status_code != HttpStatus.OK:
                raise ProductInventoryUpdateException("Ошибка при обновлении инвентаря")

            db_sale.total_price = product_data["price"] * db_sale.units_sold
            db_sale.revenue = db_sale.total_price

            db.add(db_sale)
            db.commit()
            db.refresh(db_sale)
            return db_sale

        elif current_inventory > 0:
            reduce_by = db_sale.units_sold - current_inventory
            raise InsufficientInventoryException(
                f"Недостаточно товара на складе. Уменьшите количество на {reduce_by}"
            )
        else:
            raise ProductOutofStockException("Продукт отсутствует на складе")

    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()


# Получение и агрегация статистики продаж
def fetch_sales(db: Session, product_id=None, category_id=None, user_id=None, start_date=None, end_date=None, group_by=None):
    try:
        sales_query = db.query(
            Sales.product_id,
            Sales.category_id,
            Sales.user_id,
            func.max(Sales.sold_at).label("last_sold_at"),
            func.sum(Sales.units_sold).label("total_units_sold"),
            func.sum(Sales.total_price).label("total_revenue"),
        )

        if product_id is not None:
            product_details = get_product_details_by_id(product_id)
            if product_details.status_code != HttpStatus.OK:
                raise ProductNotFoundException("Продукт не найден")
            sales_query = sales_query.filter(Sales.product_id == product_id)

        if category_id is not None:
            sales_query = sales_query.filter(Sales.category_id == category_id)

        if user_id is not None:
            sales_query = sales_query.filter(Sales.user_id == user_id)

        start_date = start_date or datetime.min
        end_date = end_date or datetime.now()
        sales_query = sales_query.filter(Sales.sold_at.between(start_date, end_date))

        if group_by:
            group_map = {
                "day": [func.DATE(Sales.sold_at)],
                "month": [func.extract("year", Sales.sold_at), func.extract("month", Sales.sold_at)],
                "year": [func.extract("year", Sales.sold_at)],
                "category": [Sales.category_id],
                "category-year": [Sales.category_id, func.extract("year", Sales.sold_at)],
                "category-month": [Sales.category_id, func.extract("year", Sales.sold_at), func.extract("month", Sales.sold_at)],
                "category-date": [Sales.category_id, func.DATE(Sales.sold_at)],
                "product_id-year": [Sales.product_id, func.extract("year", Sales.sold_at)],
                "product_id-month": [Sales.product_id, func.extract("year", Sales.sold_at), func.extract("month", Sales.sold_at)],
                "product_id-date": [Sales.product_id, func.DATE(Sales.sold_at)],
                "user": [Sales.user_id],
                "user-date": [Sales.user_id, func.DATE(Sales.sold_at)],
            }

            if group_by in group_map:
                group_fields = group_map[group_by]
                sales_query = sales_query.group_by(*group_fields)

                selected_fields = group_fields + [
                    func.max(Sales.sold_at).label("last_sold_at"),
                    func.sum(Sales.units_sold).label("total_units_sold"),
                    func.sum(Sales.total_price).label("total_revenue"),
                ]
                sales_query = sales_query.with_entities(*selected_fields)
        else:
            sales_query = sales_query.group_by(Sales.product_id, Sales.category_id, Sales.user_id, Sales.sold_at)

        print("Generated SQL:\n", sales_query.statement)
        raw_sales = sales_query.all()

        if not raw_sales:
            raise NoSalesDataFoundException("Нет данных о продажах")

        # Получение категорий и добавление имени категории
        category_map = get_all_categories()
        enriched_result = []

        for row in raw_sales:
            row_dict = row._asdict() if hasattr(row, "_asdict") else dict(row)
            row_dict["category_name"] = category_map.get(row_dict.get("category_id"), "Без категории")
            enriched_result.append(row_dict)

        return enriched_result

    except NoResultFound:
        raise ProductNotFoundException("Продукт не найден")
    except Exception as e:
        raise e
