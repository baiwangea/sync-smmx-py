import logging
from typing import Optional
from database import Database

class ProductMapper:
    def __init__(self, db: Database):
        self.db = db

    def add_mapping(self, supplier_product_id: str, local_product_id: str):
        """Adds or updates a product mapping in the database."""
        with self.db.get_db() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO product_mappings (supplier_product_id, local_product_id) VALUES (?, ?)",
                (supplier_product_id, local_product_id)
            )
            conn.commit()
            logging.info(f"Upserted mapping: {supplier_product_id} -> {local_product_id}")

    def get_mapped_product_id(self, supplier_product_id: str) -> Optional[str]:
        """Retrieves a mapped SMM-X product ID for a given supplier product ID."""
        with self.db.get_db() as conn:
            cursor = conn.execute(
                "SELECT local_product_id FROM product_mappings WHERE supplier_product_id = ?",
                (supplier_product_id,)
            )
            row = cursor.fetchone()
            if row:
                return row["local_product_id"]
            else:
                # This warning can be noisy if many products are unmapped. 
                # Consider changing level to INFO or DEBUG if needed.
                logging.warning(f"No product mapping found for supplier product ID: {supplier_product_id}")
                return None
