import logging
from typing import List, Dict
from database import Database
from api_client import ApiClient

class StatusSyncer:
    def __init__(self, db: Database, smmx_client: ApiClient):
        self.db = db
        self.smmx_client = smmx_client

    def _get_orders_to_sync(self) -> List[Dict]:
        """Fetches all orders that are not in a terminal state from the local database."""
        # Terminal states are states where the order is considered finished.
        terminal_statuses = ('Completed', 'Partial', 'Cancelled', 'Refunded', 'Error')
        query = f"SELECT id, smmx_order_id, status FROM orders WHERE status NOT IN ({','.join('?' for _ in terminal_statuses)})"
        
        with self.db.get_db() as conn:
            cursor = conn.execute(query, terminal_statuses)
            return cursor.fetchall()

    def sync_statuses(self):
        logging.info("Starting order status sync...")
        orders_to_sync = self._get_orders_to_sync()

        if not orders_to_sync:
            logging.info("No active orders to sync statuses for.")
            return

        smmx_order_ids = [str(order['smmx_order_id']) for order in orders_to_sync]
        
        # SMM-X API allows fetching multiple order statuses in one call
        smmx_payload = {
            "key": self.smmx_client.api_key,
            "action": "status",
            "orders": ",".join(smmx_order_ids)
        }
        
        statuses_response = self.smmx_client.post("", json_data=smmx_payload)

        if not statuses_response or isinstance(statuses_response, dict) and statuses_response.get("error"):
            logging.error(f"Failed to retrieve statuses from SMM-X. Response: {statuses_response}")
            return

        updates_to_commit = []
        for order in orders_to_sync:
            smmx_order_id = str(order['smmx_order_id'])
            
            if smmx_order_id in statuses_response:
                new_status = statuses_response[smmx_order_id].get('status')
                if new_status and new_status != order['status']:
                    updates_to_commit.append((new_status, order['id']))
                    logging.info(f"Status for SMM-X order {smmx_order_id} changed from '{order['status']}' to '{new_status}'.")
            else:
                logging.warning(f"SMM-X order {smmx_order_id} not found in status response.")

        if updates_to_commit:
            with self.db.get_db() as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    "UPDATE orders SET status = ? WHERE id = ?",
                    updates_to_commit
                )
                conn.commit()
            logging.info(f"Status sync finished. Updated {len(updates_to_commit)} order statuses.")
        else:
            logging.info("Status sync finished. No status changes detected.")
