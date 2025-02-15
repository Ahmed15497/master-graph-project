import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import base64
from io import BytesIO
from PIL import Image
import requests
from flask import Flask, redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

# MongoDB Connection URI
uri = "mongodb+srv://ahmedsaad22502145:mongodbmaster@cluster0.eak8u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(uri)
db = client["online_shopping"]

# Initialize Dash app
server = Flask(__name__)  # Main Flask app
server.secret_key = "supersecretkey"  # Required for session management

app = dash.Dash(__name__, server=server, routes_pathname_prefix="/", external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "E-Commerce Dashboard"


# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/"

# User Class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, email, role, first_name, last_name):
        self.id = user_id
        self.email = email
        self.role = role
        self.first_name = first_name
        self.last_name = last_name


# 🔄 Load User from MongoDB
@login_manager.user_loader
def load_user(user_id):
    user_data = db["users"].find_one({"_id": int(user_id)})
    if user_data:
        return User(user_id=user_data["_id"], email=user_data["email"], role=user_data["role"], first_name=user_data["first_name"], last_name=user_data["last_name"])
    return None


# GraphQL Endpoint
GRAPHQL_URL = "http://127.0.0.1:8000/graphql"

# Navbar with Logo
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Products", href="/products")),
        dbc.NavItem(dbc.NavLink("Admin", href="/admin")),
        dbc.NavItem(dbc.NavLink("About Us", href="/about")),
        dbc.NavItem(dbc.Button("Logout", id="logout-button")),
    ],
    brand=html.Img(src="/assets/DSAA_logo.jpeg", height="85px"),  # Adding a logo image
    brand_href="/",
    color="primary",
    dark=True,
)

# About Us Page
about_page = html.Div(
    [
        html.H1("About Us", className="text-center mt-5"),
        html.P(
            "Our vision is to create a seamless e-commerce experience for everyone.",
            className="text-center mt-3",
        ),
    ]
)

# Admin Page

admin_page = html.Div(
    [
        html.H1("Admin Dashboard", className="text-center mt-5"),
        
        # Create Product Section
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Create Product"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Label("Name"),
                                    width=4
                                ),
                                dbc.Col(
                                    dbc.Input(id="create-product-name", placeholder="Enter product name"),
                                    width=8
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Label("Description"),
                                    width=4
                                ),
                                dbc.Col(
                                    dbc.Textarea(id="create-product-description", placeholder="Enter product description"),
                                    width=8
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Label("Price"),
                                    width=4
                                ),
                                dbc.Col(
                                    dbc.Input(id="create-product-price", type="number", placeholder="Enter product price"),
                                    width=8
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Label("Stock"),
                                    width=4
                                ),
                                dbc.Col(
                                    dbc.Input(id="create-product-stock", type="number", placeholder="Enter product stock"),
                                    width=8
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Label("Category"),
                                    width=4
                                ),
                                dbc.Col(
                                    dbc.Input(id="create-product-category", placeholder="Enter product category"),
                                    width=8
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Label("Photo"),
                                    width=4
                                ),
                                dbc.Col(
                                    dcc.Upload(
                                        id="create-upload-photo",
                                        children=html.Div(["Drag and Drop or ", html.A("Select File")]),
                                        style={
                                            "width": "100%",
                                            "height": "60px",
                                            "lineHeight": "60px",
                                            "borderWidth": "1px",
                                            "borderStyle": "dashed",
                                            "borderRadius": "5px",
                                            "textAlign": "center",
                                        },
                                    ),
                                    width=8
                                ),
                            ]
                        ),
                        html.Div(id="create-photo-preview", className="mt-3"),
                        dbc.Button("Submit", id="submit-create-product", color="success", className="mt-3"),
                        html.Div(id="create-admin-output", className="mt-3"),
                    ],
                    md=6,
                ),
                


                # Update Product Section
                dbc.Col(
                    [
                        html.H3("Update Product"),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Label("Product ID"), width=4),
                                dbc.Col(dbc.Input(id="update-product-id", placeholder="Enter product ID", type="number"), width=8),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Label("Name"), width=4),
                                dbc.Col(dbc.Input(id="update-product-name", placeholder="Enter product name (optional)"), width=8),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Label("Description"), width=4),
                                dbc.Col(dbc.Textarea(id="update-product-description", placeholder="Enter product description (optional)"), width=8),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Label("Price"), width=4),
                                dbc.Col(dbc.Input(id="update-product-price", type="number", placeholder="Enter product price (optional)"), width=8),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Label("Stock"), width=4),
                                dbc.Col(dbc.Input(id="update-product-stock", type="number", placeholder="Enter product stock (optional)"), width=8),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Label("Category"), width=4),
                                dbc.Col(dbc.Input(id="update-product-category", placeholder="Enter product category (optional)"), width=8),
                            ]
                        ),
                        
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Label("Photo"),
                                    width=4
                                ),
                                dbc.Col(
                                    dcc.Upload(
                                        id="update-product-photo",
                                        children=html.Div(["Drag and Drop or ", html.A("Select File")]),
                                        style={
                                            "width": "100%",
                                            "height": "60px",
                                            "lineHeight": "60px",
                                            "borderWidth": "1px",
                                            "borderStyle": "dashed",
                                            "borderRadius": "5px",
                                            "textAlign": "center",
                                        },
                                    ),
                                    width=8
                                ),
                            ]
                        ),

                        dbc.Button("Update", id="submit-update-product", color="warning", className="mt-3"),
                        html.Div(id="update-admin-output", className="mt-3"),
                    ],
                    md=6,
                ),

                dbc.Col(
                    [
                        html.H3("Delete Product"),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Label("Product ID"), width=4),
                                dbc.Col(dbc.Input(id="delete-product-id", type="number", placeholder="Enter product ID"), width=8),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button("Delete", id="submit-delete-product", color="danger", className="mt-3"),
                                    width=12, 
                                ),
                            ]
                        ),
                        html.Div(id="delete-admin-output", className="mt-3"),
                    ],
                    md=6, 
                ),

            ]
        ),
        
        # Read All Products Section
        dbc.Button("Read All Products", id="read-all-products", color="info", className="mt-3"),
        html.Div(id="all-products-list", className="mt-3"),
    ]
)

# Products Page
products_page = html.Div(
    [
        html.H1("Products", className="text-center mt-5"),
        
        # Filters Section
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Search by Category"),
                        dbc.Input(id="search-category", placeholder="Enter category"),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("Sort By Price"),
                        dcc.Dropdown(
                            id="sort-price-options",
                            options=[
                                {"label": "Price (Ascending)", "value": "price_asc"},
                                {"label": "Price (Descending)", "value": "price_desc"},
                            ],
                            placeholder="Select price sorting option",
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("Sort By Stock"),
                        dcc.Dropdown(
                            id="sort-stock-options",
                            options=[
                                {"label": "Stock (Ascending)", "value": "stock_asc"},
                                {"label": "Stock (Descending)", "value": "stock_desc"},
                            ],
                            placeholder="Select stock sorting option",
                        ),
                    ],
                    md=4,
                ),
            ],
            className="mb-4",
        ),
        
        dcc.Interval(id="load-products-once", interval=1, n_intervals=0, max_intervals=1),  # Triggers only once
        
        html.Div(id="product-cards", className="d-flex flex-wrap justify-content-center"),
    ]
)



#Login Page
login_page = html.Div(
    [
        html.H1("Login", className="text-center mt-5"),
        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        dbc.Input(id="username", type="text", placeholder="Enter Username"),
                        width=4,
                        className="mb-3",
                    ),
                    justify="center",
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Input(id="password", type="password", placeholder="Enter Password"),
                        width=4,
                        className="mb-3",
                    ),
                    justify="center",
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Button("Login", id="login-button", color="primary", className="mt-3"),
                        width=4,
                        className="text-center",
                    ),
                    justify="center",
                ),
                html.Div(id="login-output", className="text-center mt-3"),
            ]
        ),
    ]
)



# Layout
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,
        html.Div(id="page-content"),
    ]
)



# 🔑 Login Callback
@app.callback(
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def login(n_clicks, email, password):
    user_data = db["users"].find_one({"email": email})
    
    if user_data and bcrypt.checkpw(password.encode(), user_data["hashed_password"].encode()):
        user = User(user_id=user_data["_id"], email=user_data["email"], role=user_data["role"], first_name=user_data["first_name"], last_name=user_data["last_name"])
        login_user(user)
        return dcc.Location(href="/products", id="redirect-dashboard")  # Redirect to Dashboard
    
    return "Invalid email or password!"


# 🚪 Logout Callback
@app.callback(
    Output("url", "pathname"),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def logout(n_clicks):
    logout_user()
    return "/"  # Redirect to Home Page


# Callbacks for Navigation
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/admin":
        if current_user.is_authenticated:
            return admin_page
        else:
            return login_page
    elif pathname == "/products":
        if current_user.is_authenticated:
            return products_page
        else:
            return login_page
    elif pathname == "/about":
        if current_user.is_authenticated:
            return about_page
        else:
            return login_page
    elif pathname == "/login":
        if current_user.is_authenticated:
            return products_page
        else:
            return login_page
    else:
        if current_user.is_authenticated:
            return products_page
        else:
            return login_page


# Callback to fetch all products on load or when filters are updated
@app.callback(
    Output("product-cards", "children"),
    [
        Input("load-products-once", "n_intervals"),
        Input("search-category", "value"),
        Input("sort-price-options", "value"),
        Input("sort-stock-options", "value"),
    ],
)
def update_product_cards(n_intervals, search_category, sort_price, sort_stock):
    query = """
    query {
      products {
        productId
        name
        price
        stock
        category
        photo
      }
    }
    """
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query},
        headers=headers
    )
    
    if response.status_code != 200:
        return f"Error fetching products: {response.text}"
    
    products = response.json().get("data").get("products")
    
    # Apply Filters
    if search_category:
        products = [p for p in products if search_category.lower() in p["category"].lower()]
    
    if sort_price:
        reverse = True if sort_price == "price_desc" else False
        products = sorted(products, key=lambda x: x["price"], reverse=reverse)
    
    if sort_stock:
        reverse = True if sort_stock == "stock_desc" else False
        products = sorted(products, key=lambda x: x["stock"], reverse=reverse)
    
    # Generate Product Cards
    product_cards = []
    for product in products:
        product_cards.append(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5(product["name"], className="card-title"),
                        html.P(f"Price: {product['price']} EGP", className="card-text"),
                        html.P(f"Stock: {product['stock']}", className="card-text"),
                        html.P(f"Category: {product['category']}", className="card-text"),
                        html.Img(src=f"data:image/png;base64, {product['photo']}", height="200px", width="auto"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            )
        )
    
    return product_cards

# Callback to create a new product
@app.callback(
    Output("create-admin-output", "children"),
    [
        Input("submit-create-product", "n_clicks"),
        State("create-product-name", "value"),
        State("create-product-description", "value"),
        State("create-product-price", "value"),
        State("create-product-stock", "value"),
        State("create-product-category", "value"),
        State("create-upload-photo", "contents"),
    ],
    prevent_initial_call=True,
)
def create_product(n_clicks, name, description, price, stock, category, photo):
    if n_clicks is None:
        return ""
    
    # Upload Photo Handling (if any photo is uploaded)
    if photo is not None:
        photo_content = base64.b64decode(photo.split(",")[1])
        image = Image.open(BytesIO(photo_content))
        # Process image if needed, for now, just encode it to base64
        photo = base64.b64encode(photo_content).decode("utf-8")
    
    # Create GraphQL Mutation to create product
    mutation = """
    mutation {
      createProduct(name: "%s", description: "%s", price: %f, stock: %d, category: "%s", photo: "%s") {
        name
        description
        price
        stock
        category
        photo
      }
    }
    """ % (name, description, price, stock, category, photo)
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        GRAPHQL_URL,
        json={"query": mutation},
        headers=headers
    )
    
    if response.status_code == 200:
        return f"Product '{name}' created successfully!"
    else:
        return f"Error: {response.text}"


# Callback to update an existing product
@app.callback(
    Output("update-admin-output", "children"),
    [
        Input("submit-update-product", "n_clicks"),
        State("update-product-id", "value"),
        State("update-product-name", "value"),
        State("update-product-description", "value"),
        State("update-product-price", "value"),
        State("update-product-stock", "value"),
        State("update-product-category", "value"),
        State("update-product-photo", "contents"),  # New photo input field
    ],
    prevent_initial_call=True,
)
def update_product(n_clicks, product_id, name, description, price, stock, category, photo):
    if n_clicks is None:
        return ""
    
    print(product_id, name, description, price, stock, category, photo)


    # Ensure values are valid
    #price = float(price) if price else 0.0  
    #stock = int(stock) if stock else 0 

    # GraphQL mutation including the photo field
    if photo is not None:
        photo_content = base64.b64decode(photo.split(",")[1])
        image = Image.open(BytesIO(photo_content))
        # Process image if needed, for now, just encode it to base64
        photo = base64.b64encode(photo_content).decode("utf-8")

    mutation = """
    mutation updateProduct($productId: Int!, $updates: UpdateProductInput!) {
        updateProduct(productId: $productId, updates: $updates) {
            productId
            name
            description
            price
            stock
            category
            photo
        }
    }
    """

    variables = {
        "productId": product_id,  # Replace with the actual product ID
        "updates": {
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "category": category,
            "photo": photo
        }
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(
        GRAPHQL_URL,
        json={"query": mutation, "variables": variables},
        headers=headers
    )

    if response.status_code == 200:
        return f"Product '{product_id}' updated successfully!"
    else:
        return f"Error: {response.text}"

# Callback to read all products
@app.callback(
    Output("all-products-list", "children"),
    [Input("read-all-products", "n_clicks")],
    prevent_initial_call=True,
)
def read_all_products(n_clicks):

    if n_clicks is None:
        return ""
    
    query = """
    query {
      products {
        productId
        name
        price
        stock
        category
        photo
      }
    }
    """
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query},
        headers=headers
    )
    
    if response.status_code == 200:
        products = response.json().get("data").get("products")
        product_cards = []
        for product in products:
            product_cards.append(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5(product["name"], className="card-title"),
                            html.P(f"ID: {product['productId']}", className="card-text"),
                            html.P(f"Price: {product['price']} EGP", className="card-text"),
                            html.P(f"Stock: {product['stock']}", className="card-text"),
                            html.P(f"Category: {product['category']}", className="card-text"),
                            html.Img(src=f"data:image/png;base64, {product['photo']}", height="200px", width="auto"),
                        ]
                    )
                )
            )
        return product_cards
    else:
        return f"Error: {response.text}"
    

@app.callback(
    Output("delete-admin-output", "children"),
    Input("submit-delete-product", "n_clicks"),
    State("delete-product-id", "value"),
    prevent_initial_call=True
)
def delete_product(n_clicks, product_id):
    if not product_id:
        return "Please enter a product ID."
    


    mutation = """
    mutation RemoveProduct($productId: Int!) {
        removeProduct(productId: $productId)
    }
    """

    # Define the variables
    variables = {
        "productId": product_id  # Replace with the actual product ID to delete
    }

    # Make the request
    response = requests.post(
        GRAPHQL_URL,
        json={"query": mutation, "variables": variables},
        headers={"Content-Type": "application/json"}
    )

    data = response.json()
    
    if "errors" in data:
        return f"Error: {data['errors'][0]['message']}"
    
    return f"Success"



if __name__ == "__main__":
    app.run_server(debug=True)
