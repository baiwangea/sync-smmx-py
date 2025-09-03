import sqlite3
from contextlib import contextmanager
from config import DB_FILE

class Database:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        with self.get_db() as conn:
            cursor = conn.cursor()
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_order_id TEXT UNIQUE NOT NULL,
                    smmx_order_id TEXT,
                    status TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_product_id TEXT UNIQUE NOT NULL,
                    local_product_id TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    price REAL NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_smmx_order_id ON orders (smmx_order_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_product_id ON prices (product_id)")

            # Create a trigger to automatically update `updated_at`
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_orders_updated_at
                AFTER UPDATE ON orders
                FOR EACH ROW
                BEGIN
                    UPDATE orders SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                END;
            """)
            conn.commit()

    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(self.db_file, timeout=15)  # Set a timeout
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
