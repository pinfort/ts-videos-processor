import os
from pathlib import Path

NAS_HOST = os.getenv("NAS_HOST")
NAS_USER = os.getenv("NAS_USER")
NAS_PASSWORD = os.getenv("NAS_PASSWORD")
NAS_PORT = os.getenv("NAS_PORT", 139)
NAS_NAME = os.getenv("NAS_NAME")
NAS_SERVICE_NAME = os.getenv("NAS_SERVICE_NAME")
NAS_ROOT_DIR = Path(os.getenv("NAS_ROOT_DIR"))
NAS_ROOT_DIR_ZIPED = Path(os.getenv("NAS_ROOT_DIR_ZIPED"))
