import os
from pathlib import Path

SUB_NAS_HOST = os.getenv("SUB_NAS_HOST")
SUB_NAS_USER = os.getenv("SUB_NAS_USER")
SUB_NAS_PASSWORD = os.getenv("SUB_NAS_PASSWORD")
SUB_NAS_PORT = os.getenv("SUB_NAS_PORT", 139)
SUB_NAS_NAME = os.getenv("SUB_NAS_NAME")
SUB_NAS_SERVICE_NAME = os.getenv("SUB_NAS_SERVICE_NAME")
SUB_NAS_ROOT_DIR = Path(os.getenv("NAS_ROOT_DIR"))
SUB_NAS_ROOT_DIR_ZIPED = Path(os.getenv("NAS_ROOT_DIR_ZIPED"))
