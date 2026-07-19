import os
import socket
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)

ORDERS = [
    {"id": 1001, "customer": "Demo User", "product": "Laptop", "status": "Created"}
]


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
    return jsonify(status="healthy", timestamp=datetime.now(timezone.utc).isoformat())


@app.get("/api/orders")
def list_orders():
    return jsonify(ORDERS)


@app.post("/api/orders")
def create_order():
    payload = request.get_json(silent=True) or {}
    if not payload.get("customer") or not payload.get("product"):
        return jsonify(error="customer and product are required"), 400

    order = {
        "id": max(item["id"] for item in ORDERS) + 1,
        "customer": payload["customer"],
        "product": payload["product"],
        "status": "Created",
    }
    ORDERS.append(order)
    return jsonify(order), 201


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
