# sales_service/common/custom_exceptions.py

class ProductNotFoundException(Exception):
    def __init__(self, message="Product not found"):
        self.message = message
        super().__init__(self.message)

class NoSalesDataFoundException(Exception):
    def __init__(self, message="No sales data found for the specified criteria"):
        self.message = message
        super().__init__(self.message)
