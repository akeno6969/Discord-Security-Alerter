import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("security_alerts.log")# you can customize this no problem
    ]
)

def get_logger():
    return logging.getLogger()