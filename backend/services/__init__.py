# Services Package
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.database import db_service
from services.async_queue import async_queue
from services.watchdog import watchdog_service

__all__ = ['db_service', 'async_queue', 'watchdog_service']
