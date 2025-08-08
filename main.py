# type: ignore
from mcp.server.fastmcp import FastMCP 
from dotenv import load_dotenv
from typing import Optional, Any, List
import pyodbc
import os
load_dotenv()


#Initialize the server
mcp = FastMCP("Order_Management")


def connect_to_db():
    conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=Orders;"
    "Trusted_Connection=yes;"
    )
    return conn





@mcp.tool()
async def create_order(
    customer_name: str,
    product_name: str,
    quantity: int,
    total_amount: float,
    status: str,
    order_date: str,
    shipping_address: str
) -> dict:
    """
    Use this tool to create new order for the customer.

    Parameters:
        customer_name (str): The name of the customer placing the order.
        product_name (str): The name of the product being ordered.
        quantity (int): The number of units ordered.
        total_amount (floaat): The total cost of the order.
        status (str): The current status of the order (e.g., 'processing', 'shipped', 'delivered', 'cancelled).
        order_date (str): The date and time of the order in ISO 8601 format (e.g., '2025-04-05T10:00:00Z').
        shipping_address (str): The full shipping address for the order.

    Returns:
        dict: A dictionary containing a success message confirming the order creation.
    """

    conn = connect_to_db()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO Orders (customer_name, product_name, quantity, total_amount, status, order_date, shipping_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(insert_query, (customer_name, product_name, quantity, total_amount, status, order_date, shipping_address))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Order created successfully"}




@mcp.tool()
async def read_orders() -> List[Any]:
    """
    Use this tool to fetch all customer orders from the table

    """
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "SELECT * FROM Orders"
    cursor.execute(query)
    orders = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    orders = [dict(zip(columns, row)) for row in orders]
    return orders


@mcp.tool()
async def update_order(order_id: int,
    product_name: Optional[str] = None,
    quantity: Optional[int] = None,
    status: Optional[str] = None) -> dict:

    """
    Use this tool to update existing customer order in the database.

    Parameters:
        
        customer_name Optional[str]: The name of the customer.
        product_name Optional[str]: The name of the product ordered.
        quantity Optional[str]: The quantity of the product.
        status Optional[str]: The status of the order  (e.g., 'processing', 'shipped', 'delivered', 'cancelled).

    Returns:
        dict: A message indicating that the order has been successfully updated.

    """

    conn = connect_to_db()
    fields = {"product_name": product_name, "quantity": quantity, "status": status}
    update_fields = {k: v for k, v in fields.items() if v is not None}
   
    set_clause = ", ".join([f"{key} = ?" for key in update_fields])
    values = list(update_fields.values())
    values.append(order_id)

    query = f"UPDATE Orders SET {set_clause} WHERE order_id = ?"
    
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Order updated"}



@mcp.tool()
async def delete_order(order_id: int) -> dict:
    """
    Use this tool to delete an existing customer order from the database.

    """
    conn = connect_to_db()

    cursor = conn.cursor()

    cursor.execute("DELETE FROM Orders WHERE order_id = ?", (order_id,))
    conn.commit()

    conn.close()
    return {"message": "Order deleted"}





if __name__ == "__main__":
    mcp.run(transport="stdio")




