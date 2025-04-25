import logging

def setup_logging():
    """Configure logging for the API Gateway"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("api_gateway")
    return logger