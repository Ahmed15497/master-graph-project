import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import base64
from io import BytesIO
from PIL import Image
import requests

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "E-Commerce Dashboard"

server = app.server

# GraphQL Endpoint
GRAPHQL_URL = "http://127.0.0.1:8000/graphql"

# Navbar with Logo
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Products", href="/products")),
        dbc.NavItem(dbc.NavLink("Admin", href="/admin")),
        dbc.NavItem(dbc.NavLink("About Us", href="/about")),
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
                        
                        # **Photo Upload Area**
                    dbc.Row(
                [
                    dbc.Col(dbc.Label("Product Photo"), width=4),
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
                        width=8,
                    ),
                ]
            ),

                        dbc.Button("Update", id="submit-update-product", color="warning", className="mt-3"),
                        html.Div(id="update-admin-output", className="mt-3"),
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

# Layout
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,
        html.Div(id="page-content"),
    ]
)

# Callbacks for Navigation
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/admin":
        return admin_page
    elif pathname == "/products":
        return products_page
    elif pathname == "/about":
        return about_page
    else:
        return about_page



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
        State("update-product-photo", "value"),  # New photo input field
    ],
    prevent_initial_call=True,
)
def update_product(n_clicks, product_id, name, description, price, stock, category, photo):
    if n_clicks is None:
        return ""


    # Ensure values are valid
    price = float(price) if price else 0.0  
    stock = int(stock) if stock else 0 

    # GraphQL mutation including the photo field
    mutation = """
    mutation {
      updateProduct(productId: "%d", name: "%s", description: "%s", price: %f, stock: %d, category: "%s", photo: "%s") {
        productId
        name
        price
        stock
        category
        photo
      }
    }
    """ % (product_id, name, description, price, stock, category, photo)

    headers = {"Content-Type": "application/json"}
    response = requests.post(
        GRAPHQL_URL,
        json={"query": mutation},
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

if __name__ == "__main__":
    app.run_server(debug=True)
