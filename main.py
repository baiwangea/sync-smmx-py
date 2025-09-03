import schedule
import time
import threading
import logging
from functools import wraps

# Import config variables
from config import (
    SUPPLIER_API_URL, SUPPLIER_API_KEY, SMMX_API_URL, SMMX_API_KEY,
    DB_FILE, BALANCE_LOG_FILE
)

# Import all dependencies and service classes
from database import Database
from api_client import ApiClient
from product_mapper import ProductMapper
from order_syncer import OrderSyncer
from price_syncer import PriceSyncer
from status_syncer import StatusSyncer
from balance_checker import BalanceChecker

def run_threaded(job_func):
    """Decorator that runs a job in a new thread."""
    @wraps(job_func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=job_func, args=args, kwargs=kwargs, name=job_func.__name__)
        thread.start()
    return wrapper

def safe_job(job_func):
    """Decorator that wraps a job to catch and log all exceptions."""
    @wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            job_func(*args, **kwargs)
        except Exception:
            logging.exception(f"An error occurred in job '{job_func.__name__}'")
    return wrapper

def main():
    """Initializes all components and starts the scheduler."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s"
    )
    logging.info("Starting the sync service...")

    # 1. Initialize shared dependencies once
    logging.info("Initializing dependencies...")
    db = Database(db_file=DB_FILE)
    supplier_client = ApiClient(base_url=SUPPLIER_API_URL, api_key=SUPPLIER_API_KEY)
    smmx_client = ApiClient(base_url=SMMX_API_URL, api_key=SMMX_API_KEY)
    logging.info("Dependencies initialized.")

    # 2. Initialize services using dependency injection
    logging.info("Initializing services...")
    product_mapper = ProductMapper(db=db)
    order_syncer = OrderSyncer(db=db, supplier_client=supplier_client, smmx_client=smmx_client, product_mapper=product_mapper)
    price_syncer = PriceSyncer(db=db, supplier_client=supplier_client, smmx_client=smmx_client, product_mapper=product_mapper)
    status_syncer = StatusSyncer(db=db, smmx_client=smmx_client)
    balance_checker = BalanceChecker(smmx_client=smmx_client, log_file=BALANCE_LOG_FILE)
    logging.info("Services initialized.")

    # 3. Schedule jobs to run concurrently and safely
    logging.info("Scheduling jobs...")
    schedule.every(1).minutes.do(run_threaded(safe_job(order_syncer.sync_orders)))
    schedule.every().day.at("00:00").do(run_threaded(safe_job(balance_checker.check_and_log_balance)))
    schedule.every(1).hours.do(run_threaded(safe_job(price_syncer.sync_prices)))
    schedule.every(5).minutes.do(run_threaded(safe_job(status_syncer.sync_statuses)))
    logging.info("Jobs scheduled.")

    # 4. Run the scheduler loop
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user.")
            break

if __name__ == "__main__":
    main()
