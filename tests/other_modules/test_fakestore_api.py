import requests
import pytest
import json
import logging
from pathlib import Path

# Logging is configured in pytest.ini, so we don't need to set it up here.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_payload():
    """Load test product data from JSON file."""
    with open(DATA_DIR / "product_payload.json") as f:
        return json.load(f)

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

@pytest.fixture
def product_teardown():
    """
    Fixture to register product IDs for deletion after a test.
    Call product_teardown(product_id) in your test after creating a product.
    """
    created_ids = []
    def register(product_id):
        created_ids.append(product_id)
    yield register
    for product_id in created_ids:
        url = f"https://fakestoreapi.com/products/{product_id}"
        response = requests.delete(url)
        log_request_response("DELETE (teardown)", url, None, response)

class TestFakeStoreAPI:
    def test_get_product(self):
        """Test retrieving a single product by ID."""
        url = "https://fakestoreapi.com/products/1"
        response = requests.get(url)
        log_request_response("GET", url, None, response)
        assert response.status_code == 200
        data = response.json()
        assert data.get("id") == 1
        assert "title" in data

    def test_post_product(self, product_teardown):
        """Test creating a new product."""
        url = "https://fakestoreapi.com/products"
        payload = load_payload()
        response = requests.post(url, json=payload)
        log_request_response("POST", url, payload, response)
        assert response.status_code in (200, 201)
        data = response.json()
        assert data.get("title") == payload["title"]
        assert data.get("category") == payload["category"]
        product_id = data.get("id")
        assert product_id is not None
        product_teardown(product_id)  # Register for cleanup

    def test_put_product(self, product_teardown):
        """Test updating an existing product."""
        # First, create a product to update
        url = "https://fakestoreapi.com/products"
        payload = load_payload()
        post_response = requests.post(url, json=payload)
        log_request_response("POST (setup)", url, payload, post_response)
        assert post_response.status_code in (200, 201)
        data = post_response.json()
        product_id = data.get("id")
        assert product_id is not None
        product_teardown(product_id)  # Register for cleanup

        # Now, update it with PUT
        put_url = f"{url}/{product_id}"
        updated_payload = payload.copy()
        updated_payload["title"] = "Updated Product Title"
        put_response = requests.put(put_url, json=updated_payload)
        log_request_response("PUT", put_url, updated_payload, put_response)
        assert put_response.status_code == 200
        updated = put_response.json()
        assert updated.get("title") == "Updated Product Title"

    def test_delete_product(self):
        """Test deleting a product."""
        # First, create a product to delete
        url = "https://fakestoreapi.com/products"
        payload = load_payload()
        post_response = requests.post(url, json=payload)
        log_request_response("POST (setup)", url, payload, post_response)
        assert post_response.status_code in (200, 201)
        data = post_response.json()
        product_id = data.get("id")
        assert product_id is not None

        # Now, delete it
        del_url = f"{url}/{product_id}"
        del_response = requests.delete(del_url)
        log_request_response("DELETE", del_url, None, del_response)
        assert del_response.status_code == 200
        deleted = del_response.json()
        assert str(deleted.get("id")) == str(product_id)

# Add config changes
