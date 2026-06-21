import logging
import sys

# Configure logging format
logging_format = (
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)

logging.basicConfig(
    level=logging.INFO,
    format=logging_format,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("golden_minute")
