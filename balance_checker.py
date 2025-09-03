import logging
from datetime import datetime
from typing import Optional
from api_client import ApiClient

class BalanceChecker:
    def __init__(self, smmx_client: ApiClient, log_file: str):
        self.smmx_client = smmx_client
        self.log_file = log_file

    def _get_balance(self) -> Optional[str]:
        """Fetches the current balance from the SMM-X API."""
        payload = {
            "key": self.smmx_client.api_key,
            "action": "balance"
        }
        response = self.smmx_client.post("", json_data=payload)
        
        if response and "balance" in response and "currency" in response:
            return f"{response['balance']} {response['currency']}"
        else:
            logging.error(f"Failed to retrieve balance. Response: {response}")
            return None

    def check_and_log_balance(self):
        """Checks the balance and logs it to the specified file."""
        logging.info("Checking SMM-X account balance...")
        balance = self._get_balance()
        
        if balance:
            log_entry = f"{datetime.now().isoformat()} - Balance: {balance}\n"
            try:
                with open(self.log_file, "a") as f:
                    f.write(log_entry)
                logging.info(f"Successfully logged balance: {balance}")
            except IOError as e:
                logging.error(f"Failed to write to balance log file {self.log_file}: {e}")
