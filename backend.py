import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from fastapi import FastAPI, Request
import uvicorn
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId to handle MongoDB's _id

# Database setup
client = MongoClient("mongodb://localhost:27017/")
db = client["online_shopping"]
products_collection = db["products"]

# Product GraphQL Types
@strawberry.type
class ProductType:
    product_id: str  # Change to string to represent ObjectId as string
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    photo: Optional[str]

    # Convert MongoDB ObjectId to string when returning product data
    @staticmethod
    def from_mongo(product):
        return ProductType(
            product_id=str(product["_id"]),  # Convert ObjectId to string
            name=product["name"],
            description=product.get("description"),
            price=product["price"],
            stock=product["stock"],
            category=product.get("category"),
            photo=product.get("photo"),
        )

@strawberry.input
class UpdateProductInput:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    photo: Optional[str] = None

# Query Resolvers
@strawberry.type
class Query:
    @strawberry.field
    def products(self, info) -> List[ProductType]:
        products = products_collection.find()
        return [ProductType.from_mongo(product) for product in products]

    @strawberry.field
    def product(self, product_id: str, info) -> Optional[ProductType]:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return None
        return ProductType.from_mongo(product)

# Mutation Resolvers
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(
        self,
        name: str,
        description: Optional[str],
        price: float,
        stock: int,
        category: Optional[str] = None,
        photo: Optional[str] = None,
    ) -> ProductType:
        product = {
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "category": category,
            "photo": photo,
        }
        result = products_collection.insert_one(product)
        product["_id"] = result.inserted_id  # Add the MongoDB _id to the product
        return ProductType.from_mongo(product)

    @strawberry.mutation
    def update_product(
        self, product_id: str, updates: UpdateProductInput, info
    ) -> Optional[ProductType]:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return None

        # Convert updates to dictionary and remove None values
        update_data = {k: v for k, v in updates.__dict__.items() if v is not None}
        products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})

        updated_product = products_collection.find_one({"_id": ObjectId(product_id)})
        return ProductType.from_mongo(updated_product)

    @strawberry.mutation
    def delete_product(self, product_id: str, info) -> bool:
        result = products_collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0

# Define a custom context function
def get_context(request: Request) -> dict:
    return {"request": request}

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

# FastAPI app
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
