# --- utils/logger.py ---
from loguru import logger
import sys, os

# Remove default logger and add ours (timestamp | level | module:function | message)
logger.remove()
fmt = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
    "<level>{message}</level>"
)
logger.add(sys.stdout, colorize=True, format=fmt, enqueue=True)

# Optional rotating log file (10 MB each, keep 10 files)
LOG_FILE = os.getenv("LOG_FILE", "agent.log")
logger.add(LOG_FILE, rotation="10 MB", retention="10 days", enqueue=True)
