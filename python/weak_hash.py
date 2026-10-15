import hashlib

DB_PASSWORD = "SuperSecret123!"      # 🚩
API_KEY = "sk-live-abc123..."        # 🚩
AWS_SECRET = "AKIA..."               # 🚩

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()  # 🚩

import logging

def login(username, password):
    logging.info(f"Login attempt user={username} pass={password}")  # 🚩
