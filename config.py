import os

SUPPLIER_API_URL = os.getenv("SUPPLIER_API_URL", "https://console-docs.apipost.cn/preview/bd5562d43f91d43b/2c389668408f0236?target_id=9002ae07-1333-4182-b39b-2e77c9ee8ddd")
SUPPLIER_API_KEY = os.getenv("SUPPLIER_API_KEY")

SMMX_API_URL = os.getenv("SMMX_API_URL", "https://smm-x.com/api")
SMMX_API_KEY = os.getenv("SMMX_API_KEY", "*************************")

DB_FILE = os.getenv("DB_FILE", "database.sqlite")
BALANCE_LOG_FILE = os.getenv("BALANCE_LOG_FILE", "balance_log.txt")
