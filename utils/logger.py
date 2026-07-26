"""
Logging module for AI Behavioral Anomaly Detection System.
"""

import logging
import sys


def setup_logger(name: str = "AnomalyDetection") -> logging.Logger:
    """Configures structured console logging."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
