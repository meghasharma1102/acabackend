import os
import socket
from datetime import datetime, timezone

import pymysql
from pymysql.cursors import DictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "q1-sql-server.mysql.database.azure.com"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "ms"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "q1-order-db"),
    "ssl": {} if os.getenv("DB_SSL_MODE", "require") == "require" else None,
    "cursorclass": DictCursor,
}


def get_connection():
    config = {key: value for key, value in DB_CONFIG.items() if value is not None}
    return pymysql.connect(**config)


def init_db():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer VARCHAR(100) NOT NULL,
                    product VARCHAR(100) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'Created',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                ) AUTO_INCREMENT = 1001
                """
            )
            cursor.execute("SELECT COUNT(*) AS total FROM orders")
            if cursor.fetchone()["total"] == 0:
                cursor.execute(
                    """
                    INSERT INTO orders (customer, product, status)
                    VALUES (%s, %s, %s)
                    """,
                    ("Demo User", "Laptop", "Created"),
                )
        connection.commit()


init_db()


@app.get("/")
def home():
    return jsonify(
        application="ACA Order API",
        version=os.getenv("APP_VERSION", "v1"),
        environment=os.getenv("APP_ENV", "local"),
        hostname=socket.gethostname(),
    )


@app.get("/health")
def health():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS ok")
                cursor.fetchone()
        database = "connected"
    except Exception as exc:
        return (
            jsonify(
                status="unhealthy",
                database="disconnected",
                error=str(exc),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            500,
        )

    return jsonify(
        status="healthy",
        database=database,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/orders")
def list_orders():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, customer, product, status
                FROM orders
                ORDER BY id
                """
            )
            orders = cursor.fetchall()
    return jsonify(orders)


@app.post("/api/orders")
def create_order():
    payload = request.get_json(silent=True) or {}
    if not payload.get("customer") or not payload.get("product"):
        return jsonify(error="customer and product are required"), 400

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO orders (customer, product, status)
                VALUES (%s, %s, %s)
                """,
                (payload["customer"], payload["product"], "Created"),
            )
            order_id = cursor.lastrowid
            cursor.execute(
                """
                SELECT id, customer, product, status
                FROM orders
                WHERE id = %s
                """,
                (order_id,),
            )
            order = cursor.fetchone()
        connection.commit()
    return jsonify(order), 201


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
