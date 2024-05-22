import os
import sys
import logging

# format log string to include time file name and custom message
logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"

# Create log folder and setup log file
log_dir = "logs"
log_filepath = os.path.join(log_dir, "running_logs.log")
os.makedirs(log_dir, exist_ok=True)

# config for log file
logging.basicConfig(
    level=logging.INFO,
    format=logging_str,

    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("cnnClassifierLogger")
