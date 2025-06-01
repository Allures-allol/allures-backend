import strawberry
from sqlalchemy.orm import Session
from common.db.session import SessionLocal
from common.models.products import Product as ProductModel
from services.review_service.models.review import Review as ReviewModel
from services.review_service.models.recommendation import Recommendation as RecommendationModel

@strawberry.type
class Product:
    id: int
    name: str
    description: str
    price: float
    image: str
    category_name: str
    created_at: str
    updated_at: str
    status: str
    current_inventory: int

@strawberry.type
class Review:
    id: int
    product_id: int
    user_id: int
    text: str
    sentiment: str
    pos_score: float
    neg_score: float
    created_at: str

@strawberry.type
class Recommendation:
    id: int
    user_id: int
    product_id: int
    score: float

@strawberry.type
class Query:
    @strawberry.field
    def products(self) -> list[Product]:
        with SessionLocal() as db:
            result = db.query(ProductModel).all()
            return [
                Product(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    price=p.price,
                    image=p.image,
                    category_name=p.category.category_name if p.category else "Unknown",
                    created_at=str(p.created_at),
                    updated_at=str(p.updated_at),
                    status=p.status,
                    current_inventory=p.current_inventory
                ) for p in result
            ]

    @strawberry.field
    def reviews(self) -> list[Review]:
        with SessionLocal() as db:
            result = db.query(ReviewModel).all()
            return [
                Review(
                    id=r.id, product_id=r.product_id, user_id=r.user_id,
                    text=r.text, sentiment=r.sentiment,
                    pos_score=r.pos_score, neg_score=r.neg_score,
                    created_at=str(r.created_at)
                ) for r in result
            ]

    @strawberry.field
    def recommendations(self) -> list[Recommendation]:
        with SessionLocal() as db:
            result = db.query(RecommendationModel).all()
            return [
                Recommendation(
                    id=r.id, user_id=r.user_id,
                    product_id=r.product_id, score=r.score
                ) for r in result
            ]

schema = strawberry.Schema(query=Query)



# === Рекомендации ===
class RecommendationOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    score: float
    recommended_at: datetime

    class Config:
        from_attributes = True


# === Поисковый запрос и вывод ===
class QueryRequest(BaseModel):
    query: str

class ProductOut(BaseModel):
    id: int
    name: str
    sentiment_score: float
    pos_percent: float
