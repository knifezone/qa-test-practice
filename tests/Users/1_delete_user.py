import json
import logging
from pathlib import Path
import requests
import pytest

# Logging is configured in pytest.ini, so we don't need to set it up here.
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

def log_request_response(method, url, req_body, response):
    """Log the request and response details."""
    logging.info(f"REQUEST: {method} {url}")
    if req_body is not None:
        logging.info(f"REQUEST BODY: {json.dumps(req_body, indent=2)}")
    logging.info(f"RESPONSE STATUS: {response.status_code}")
    try:
        logging.info(f"RESPONSE JSON: {json.dumps(response.json(), indent=2)}")
    except Exception:
        logging.info(f"RESPONSE TEXT: {response.text}")


def test_delete():
    url = "https://fakestoreapi.com/users/1"
    response = requests.delete(url)
    log_request_response("DELETE", url, None, response)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data.get("id") == 1
