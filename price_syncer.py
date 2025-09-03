import logging
from database import Database
from api_client import ApiClient
from product_mapper import ProductMapper

class PriceSyncer:
    def __init__(self, db: Database, supplier_client: ApiClient, smmx_client: ApiClient, product_mapper: ProductMapper):
        self.db = db
        self.supplier_client = supplier_client
        self.smmx_client = smmx_client
        self.product_mapper = product_mapper

    def sync_prices(self):
        logging.info("Starting price sync...")
        prices_response = self.supplier_client.get("/prices")
        if not prices_response or "data" not in prices_response:
            logging.warning("No prices retrieved from supplier or malformed response.")
            return

        updated_count = 0
        with self.db.get_db() as conn:
            for price_data in prices_response["data"]:
                supplier_product_id = price_data.get("product_id")
                new_price = price_data.get("price")

                if not supplier_product_id or new_price is None:
                    logging.warning(f"Skipping price update for invalid data: {price_data}")
                    continue

                cursor = conn.execute(
                    "SELECT price FROM prices WHERE product_id = ?", (supplier_product_id,)
                )
                row = cursor.fetchone()
                current_price = row["price"] if row else None

                if current_price != new_price:
                    mapped_product_id = self.product_mapper.get_mapped_product_id(supplier_product_id)
                    if not mapped_product_id:
                        continue

                    smmx_payload = {
                        "key": self.smmx_client.api_key,
                        "action": "update_price",
                        "service": mapped_product_id,
                        "price": new_price
                    }
                    smmx_response = self.smmx_client.post("", json_data=smmx_payload)

                    if smmx_response and not smmx_response.get("error"):
                        cursor.execute(
                            "INSERT OR REPLACE INTO prices (product_id, price) VALUES (?, ?)",
                            (supplier_product_id, new_price)
                        )
                        updated_count += 1
                        logging.info(f"Updated price for supplier product {supplier_product_id} to {new_price}")
                    else:
                        logging.error(f"Failed to update price for SMM-X service {mapped_product_id}. Response: {smmx_response}")
            
            if updated_count > 0:
                conn.commit()
        
        logging.info(f"Price sync finished. Updated {updated_count} prices.")
