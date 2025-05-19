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

# Функция для получения данных о продукте
def get_product_details_by_id(product_id: int):
    base_path = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8000")
    url = f"{base_path}/products/get_product/?product_id={product_id}"
    print("Requesting product details from product service at:", url)
    return requests.get(url=url)

# Функция для обновления инвентаря продукта
def decrement_product_inventory(new_quantity: int, product_id: int):
    base_path = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8000")
    url = f"{base_path}/products/update/?product_id={product_id}"
    update_body = {"current_inventory": new_quantity}
    return requests.put(url=url, json=update_body)

# Функция для создания транзакции продажи
def create_product_sale_transaction(sale: Sales, db: Session):
    try:
        db_sale = Sales(**sale.dict())
        print("Payload received:", vars(db_sale))

        product_response = get_product_details_by_id(db_sale.product_id)
        if product_response.status_code != HttpStatus.OK:
            raise ProductNotFoundException("Product not found")

        product_data = product_response.json()
        current_inventory = product_data.get("current_inventory", 0)

        if current_inventory >= db_sale.units_sold:
            new_inventory = current_inventory - db_sale.units_sold
            inventory_update = decrement_product_inventory(new_inventory, db_sale.product_id)

            if inventory_update.status_code != HttpStatus.OK:
                raise ProductInventoryUpdateException("Error updating inventory")

            db_sale.total_price = product_data["price"] * db_sale.units_sold
            db_sale.revenue = db_sale.total_price

            db.add(db_sale)
            db.commit()
            db.refresh(db_sale)
            return db_sale

        elif current_inventory > 0:
            reduce_by = db_sale.units_sold - current_inventory
            raise InsufficientInventoryException(
                f"Insufficient inventory. Reduce quantity by {reduce_by}"
            )
        else:
            raise ProductOutofStockException("Product is out of stock")

    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Функция для выборки данных о продажах
def fetch_sales(db: Session, product_id=None, category=None, start_date=None, end_date=None, group_by=None):
    try:
        sales_query = db.query(
            Sales.product_id,
            Sales.category_name,
            func.max(Sales.sold_at).label("last_sold_at"),
            func.sum(Sales.units_sold).label("total_units_sold"),
            func.sum(Sales.total_price).label("total_revenue"),
        )

        if product_id is not None:
            product_details = get_product_details_by_id(product_id)
            if product_details.status_code != HttpStatus.OK:
                raise ProductNotFoundException("Product not found")
            sales_query = sales_query.filter(Sales.product_id == product_id)

        if category is not None:
            sales_query = sales_query.filter(Sales.category_name == category)

        start_date = start_date or datetime.min
        end_date = end_date or datetime.now()
        sales_query = sales_query.filter(Sales.sold_at.between(start_date, end_date))

        # Группировка по различным полям
        if group_by:
            group_map = {
                "day": [func.DATE(Sales.sold_at)],
                "month": [func.YEAR(Sales.sold_at), func.MONTH(Sales.sold_at)],
                "year": [func.YEAR(Sales.sold_at)],
                "category": [Sales.category_name],
                "category-year": [Sales.category_name, func.extract("year", Sales.sold_at)],
                "category-month": [Sales.category_name, func.extract("year", Sales.sold_at), func.extract("month", Sales.sold_at)],
                "category-date": [Sales.category_name, func.DATE(Sales.sold_at)],
                "product_id-year": [Sales.product_id, func.extract("year", Sales.sold_at)],
                "product_id-month": [Sales.product_id, func.extract("year", Sales.sold_at), func.extract("month", Sales.sold_at)],
                "product_id-date": [Sales.product_id, func.DATE(Sales.sold_at)],
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
            sales_query = sales_query.group_by(Sales.product_id, Sales.category_name, Sales.sold_at)

        print("Generated SQL:\n", sales_query.statement)
        result = sales_query.all()

        if not result:
            raise NoSalesDataFoundException("No sales data found")

        return result

    except NoResultFound as e:
        raise ProductNotFoundException("Product not found") from e

    except Exception as e:
        raise e
