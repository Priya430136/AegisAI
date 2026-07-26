"""
Utility functions for metrics calculation, JSON formatting, and model persistence.
"""

import json
import os
import pickle
from typing import Dict, Any


def save_json(data: Dict[str, Any], file_path: str):
    """Saves dictionary to formatted JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def load_json(file_path: str) -> Dict[str, Any]:
    """Loads JSON file into dictionary."""
    with open(file_path, "r") as f:
        return json.load(f)


def save_model(model_obj: Any, file_path: str):
    """Pickles Python object to disk."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        pickle.dump(model_obj, f)


def load_model(file_path: str) -> Any:
    """Unpickles model from disk."""
    with open(file_path, "rb") as f:
        return pickle.load(f)
