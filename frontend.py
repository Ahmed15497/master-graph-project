import dash
from dash import dcc, html, Input, Output, State
import requests

# GraphQL API endpoint
GRAPHQL_URL = "http://127.0.0.1:8000/graphql"

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Online Shopping - Product Management"),
    html.Div([
        html.H3("Add Product"),
        html.Div([
            "Name: ", dcc.Input(id="add-name", type="text"),
            "Description: ", dcc.Input(id="add-description", type="text"),
            "Price: ", dcc.Input(id="add-price", type="number"),
            "Stock: ", dcc.Input(id="add-stock", type="number"),
            html.Button("Add Product", id="add-button"),
        ]),
        html.Div(id="add-output"),
    ]),
    html.Hr(),
    html.Div([
        html.H3("Update Product"),
        html.Div([
            "Product ID: ", dcc.Input(id="update-id", type="number"),
            "Name: ", dcc.Input(id="update-name", type="text"),
            "Description: ", dcc.Input(id="update-description", type="text"),
            "Price: ", dcc.Input(id="update-price", type="number"),
            "Stock: ", dcc.Input(id="update-stock", type="number"),
            html.Button("Update Product", id="update-button"),
        ]),
        html.Div(id="update-output"),
    ]),
    html.Hr(),
    html.Div([
        html.H3("Delete Product"),
        html.Div([
            "Product ID: ", dcc.Input(id="delete-id", type="number"),
            html.Button("Delete Product", id="delete-button"),
        ]),
        html.Div(id="delete-output"),
    ]),
    html.Hr(),
    html.Div([
        html.H3("Product List"),
        html.Button("Refresh List", id="refresh-button"),
        html.Div(id="product-list"),
    ]),
])

# Callbacks

# Add Product
@app.callback(
    Output("add-output", "children"),
    Input("add-button", "n_clicks"),
    State("add-name", "value"),
    State("add-description", "value"),
    State("add-price", "value"),
    State("add-stock", "value"),
)
def add_product(n_clicks, name, description, price, stock):
    if n_clicks:
        query = """
        mutation CreateProduct($name: String!, $description: String, $price: Float!, $stock: Int!) {
            createProduct(name: $name, description: $description, price: $price, stock: $stock) {
                productId
                name
            }
        }
        """
        variables = {"name": name, "description": description, "price": price, "stock": stock}
        response = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables})
        data = response.json()
        if "errors" in data:
            return f"Error: {data['errors'][0]['message']}"
        return f"Product Added: {data['data']['createProduct']['name']}"
    return ""

# Update Product
@app.callback(
    Output("update-output", "children"),
    Input("update-button", "n_clicks"),
    State("update-id", "value"),
    State("update-name", "value"),
    State("update-description", "value"),
    State("update-price", "value"),
    State("update-stock", "value"),
)
def update_product(n_clicks, product_id, name, description, price, stock):
    if n_clicks:
        query = """
        mutation UpdateProduct($productId: Int!, $name: String!, $description: String, $price: Float!, $stock: Int!) {
            updateProduct(productId: $productId, name: $name, description: $description, price: $price, stock: $stock) {
                name
            }
        }
        """
        variables = {"productId": product_id, "name": name, "description": description, "price": price, "stock": stock}
        response = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables})
        data = response.json()
        if "errors" in data:
            return f"Error: {data['errors'][0]['message']}"
        return f"Product Updated: {data['data']['updateProduct']['name']}"
    return ""

# Delete Product
@app.callback(
    Output("delete-output", "children"),
    Input("delete-button", "n_clicks"),
    State("delete-id", "value"),
)
def delete_product(n_clicks, product_id):
    if n_clicks:
        query = """
        mutation DeleteProduct($productId: Int!) {
            deleteProduct(productId: $productId)
        }
        """
        variables = {"productId": product_id}
        response = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables})
        data = response.json()
        if "errors" in data:
            return f"Error: {data['errors'][0]['message']}"
        return "Product Deleted" if data["data"]["deleteProduct"] else "Error: Product Not Found"
    return ""

# List Products
@app.callback(
    Output("product-list", "children"),
    Input("refresh-button", "n_clicks"),
)
def list_products(n_clicks):
    if n_clicks:
        query = """
        query {
            products {
                productId
                name
                description
                price
                stock
            }
        }
        """
        response = requests.post(GRAPHQL_URL, json={"query": query})
        data = response.json()
        if "errors" in data:
            return f"Error: {data['errors'][0]['message']}"
        products = data["data"]["products"]
        return html.Ul([html.Li(f"{p['name']} - ${p['price']} - Stock: {p['stock']}") for p in products])
    return "Click 'Refresh List' to load products."

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port = 8050)