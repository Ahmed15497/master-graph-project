import strawberry
from strawberry.fastapi import GraphQLRouter
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base
from typing import List, Optional
from fastapi import FastAPI, Depends
import uvicorn
from fastapi import Request
from sqlalchemy.orm import Session

# Database setup
DATABASE_URL = "mysql+mysqlconnector://ahmed:ahmed@localhost/online_shopping"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Product model
class Product(Base):
    __tablename__ = "products"  # Corrected: double underscores
    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GraphQL schema
@strawberry.type
class ProductType:
    product_id: int
    name: str
    description: Optional[str]
    price: float
    stock: int

@strawberry.type
class Query:
    @strawberry.field
    def products(self, info) -> List[ProductType]:
        db: Session = info.context["db"]  # Access the database session from the context
        products = db.query(Product).all()
        return [
            ProductType(
                product_id=product.product_id,
                name=product.name,
                description=product.description,
                price=product.price,
                stock=product.stock,
            )
            for product in products
        ]

    @strawberry.field
    def product(self, product_id: int, info) -> Optional[ProductType]:
        db: Session = info.context["db"]
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return None
        return ProductType(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
        )


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(
        self, name: str, description: Optional[str], price: float, stock: int, info
    ) -> ProductType:
        print('###############')
        print(info.context)
        print('###############')
        db: Session = info.context["db"]
        product = Product(name=name, description=description, price=price, stock=stock)
        db.add(product)
        db.commit()
        db.refresh(product)
        return ProductType(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
        )

    @strawberry.mutation
    def update_product(
        self,
        product_id: int,
        name: str,
        description: Optional[str],
        price: float,
        stock: int,
        info,
    ) -> Optional[ProductType]:
        db: Session = info.context["db"]
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return None
        product.name = name
        product.description = description
        product.price = price
        product.stock = stock
        db.commit()
        db.refresh(product)
        return ProductType(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
        )

    @strawberry.mutation
    def delete_product(self, product_id: int, info) -> bool:
        db: Session = info.context["db"]
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return False
        db.delete(product)
        db.commit()
        return True
    


# Define a custom context function
# Dependency for creating context
def get_context(request: Request) -> dict:
    db: Session = SessionLocal()  # Create a new DB session
    return {"request": request, "db": db}


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)


# FastAPI app
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    # Blocking behavior
    uvicorn.run(app, host="0.0.0.0", port=8000)