# import strawberry
# from strawberry.fastapi import GraphQLRouter
# from typing import List, Optional
# from fastapi import FastAPI, Request
# import uvicorn
# from pymongo import MongoClient
# from bson import ObjectId  # Import ObjectId to handle MongoDB's _id

# # Database setup
# # client = MongoClient("mongodb://localhost:27017")
# # client = MongoClient("mongodb+srv://alaabassem669:<db_password>@cluster0.xkee3.mongodb.net/")

# client = MongoClient("mongodb://localhost:27017/")

# # Check available databases
# print("Databases:", client.list_database_names())

# db = client["online_shopping"]
# products_collection = db["products"]

# # Product GraphQL Types
# @strawberry.type
# class ProductType:
#     product_id: str  # Change to string to represent ObjectId as string
#     name: str
#     description: Optional[str]
#     price: float
#     stock: int
#     category: Optional[str]
#     photo: Optional[str]

#     # Convert MongoDB ObjectId to string when returning product data
#     @staticmethod
#     def from_mongo(product):
#         return ProductType(
#             product_id=str(product["_id"]),  # Convert ObjectId to string
#             name=product["name"],
#             description=product.get("description"),
#             price=product["price"],
#             stock=product["stock"],
#             category=product.get("category"),
#             photo=product.get("photo"),
#         )

# @strawberry.input
# class UpdateProductInput:
#     name: Optional[str] = None
#     description: Optional[str] = None
#     price: Optional[float] = None
#     stock: Optional[int] = None
#     category: Optional[str] = None
#     photo: Optional[str] = None

# # Query Resolvers
# @strawberry.type
# class Query:
#     @strawberry.field
#     def products(self, info) -> List[ProductType]:
#         products = products_collection.find()
#         return [ProductType.from_mongo(product) for product in products]

#     @strawberry.field
#     def product(self, product_id: str, info) -> Optional[ProductType]:
#         product = products_collection.find_one({"_id": ObjectId(product_id)})
#         if not product:
#             return None
#         return ProductType.from_mongo(product)

# # Mutation Resolvers
# @strawberry.type
# class Mutation:
#     @strawberry.mutation
#     def create_product(
#         self,
#         name: str,
#         description: Optional[str],
#         price: float,
#         stock: int,
#         category: Optional[str] = None,
#         photo: Optional[str] = None,
#     ) -> ProductType:
#         product = {
#             "name": name,
#             "description": description,
#             "price": price,
#             "stock": stock,
#             "category": category,
#             "photo": photo,
#         }
#         result = products_collection.insert_one(product)
#         product["_id"] = result.inserted_id  # Add the MongoDB _id to the product
#         return ProductType.from_mongo(product)

#     @strawberry.mutation
#     def update_product(
#         self, product_id: str, updates: UpdateProductInput, info
#     ) -> Optional[ProductType]:
#         product = products_collection.find_one({"_id": ObjectId(product_id)})
#         if not product:
#             return None

#         # Convert updates to dictionary and remove None values
#         update_data = {k: v for k, v in updates.__dict__.items() if v is not None}
#         products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})

#         updated_product = products_collection.find_one({"_id": ObjectId(product_id)})
#         return ProductType.from_mongo(updated_product)

#     @strawberry.mutation
#     def delete_product(self, product_id: str, info) -> bool:
#         result = products_collection.delete_one({"_id": ObjectId(product_id)})
#         return result.deleted_count > 0

# # Define a custom context function
# def get_context(request: Request) -> dict:
#     return {"request": request}

# schema = strawberry.Schema(query=Query, mutation=Mutation)
# graphql_app = GraphQLRouter(schema, context_getter=get_context)

# # FastAPI app
# app = FastAPI()
# app.include_router(graphql_app, prefix="/graphql")

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)





import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from fastapi import FastAPI, Request
import uvicorn
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://ahmedsaad22502145:mongodbmaster@cluster0.eak8u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Database setup
#client = MongoClient("mongodb://localhost:27017/")
db = client["online_shopping"]
products_collection = db["products"]
counters_collection = db["counters"]  # Collection to store auto-increment IDs

# Function to get the next sequence number for products
def get_next_sequence(name: str) -> int:
    counter = counters_collection.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return counter["seq"]

# Product GraphQL Types
@strawberry.type
class ProductType:
    product_id: int  # Change to int instead of ObjectId
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    photo: Optional[str]

    @staticmethod
    def from_mongo(product):
        return ProductType(
            product_id=product["_id"],  # Use integer ID instead of ObjectId
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
    def product(self, product_id: int, info) -> Optional[ProductType]:
        product = products_collection.find_one({"_id": product_id})
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
        product_id = get_next_sequence("product_id")  # Generate auto-incrementing ID
        product = {
            "_id": product_id,
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "category": category,
            "photo": photo,
        }
        products_collection.insert_one(product)
        return ProductType.from_mongo(product)

    @strawberry.mutation
    def update_product(self, product_id: int, updates: UpdateProductInput, info) -> Optional[ProductType]:
        try:
            print("update_product function is being called!")
            print(f"Received product_id: {product_id}")

            product = products_collection.find_one({"_id": product_id})
            print("Queried product:", product)

            if not product:
                print(f"Product with ID {product_id} not found!")
                return None

            update_data = {k: v for k, v in updates.__dict__.items() if v is not None}
            print("🔍 Update data:", update_data)

            if not update_data:
                print("No updates provided!")
                return None

            result = products_collection.update_one({"_id": product_id}, {"$set": update_data})
            print("MongoDB update result:", result.raw_result)

            if result.modified_count == 0:
                print("Update failed! No changes were made.")
                return None

            updated_product = products_collection.find_one({"_id": product_id})
            print("Updated product:", updated_product)

            return ProductType.from_mongo(updated_product)

        except Exception as e:
            print(f"ERROR: {e}")
            return None



    @strawberry.mutation
    def delete_product(self, product_id: int, info) -> bool:
        result = products_collection.delete_one({"_id": product_id})
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
