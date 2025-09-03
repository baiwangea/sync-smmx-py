import logging
from database import Database
from api_client import ApiClient
from product_mapper import ProductMapper

class OrderSyncer:
    def __init__(self, db: Database, supplier_client: ApiClient, smmx_client: ApiClient, product_mapper: ProductMapper):
        self.db = db
        self.supplier_client = supplier_client
        self.smmx_client = smmx_client
        self.product_mapper = product_mapper

    def sync_orders(self):
        logging.info("Starting order sync...")
        orders_response = self.supplier_client.get("/orders")
        if not orders_response or "data" not in orders_response:
            logging.warning("No orders retrieved from supplier or malformed response.")
            return

        new_orders_count = 0
        with self.db.get_db() as conn:
            for order in orders_response["data"]:
                supplier_order_id = order.get("id")
                if not supplier_order_id:
                    logging.warning(f"Skipping order with missing id: {order}")
                    continue

                cursor = conn.execute(
                    "SELECT 1 FROM orders WHERE supplier_order_id = ?", (supplier_order_id,)
                )
                if cursor.fetchone():
                    continue

                supplier_product_id = order.get("product_id")
                if not supplier_product_id:
                    logging.warning(f"Skipping order {supplier_order_id} with missing product_id.")
                    continue
                
                mapped_product_id = self.product_mapper.get_mapped_product_id(supplier_product_id)
                if not mapped_product_id:
                    continue

                smmx_payload = {
                    "key": self.smmx_client.api_key,
                    "action": "add",
                    "service": mapped_product_id,
                    "quantity": order.get("quantity"),
                }
                
                smmx_response = self.smmx_client.post("", json_data=smmx_payload)

                if smmx_response and "order" in smmx_response:
                    smmx_order_id = smmx_response["order"]
                    cursor.execute(
                        "INSERT INTO orders (supplier_order_id, smmx_order_id, status) VALUES (?, ?, ?)",
                        (supplier_order_id, smmx_order_id, "pending")
                    )
                    new_orders_count += 1
                    logging.info(f"Synced supplier order {supplier_order_id} to SMM-X order {smmx_order_id}")
                else:
                    logging.error(f"Failed to place order {supplier_order_id} on SMM-X. Response: {smmx_response}")

            if new_orders_count > 0:
                conn.commit()
        
        logging.info(f"Order sync finished. Synced {new_orders_count} new orders.")
