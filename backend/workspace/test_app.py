import os
import pytest
from fastapi.testclient import TestClient

import math_lib
import database
from main import app

@pytest.fixture(autouse=True)
def setup_database():
    if os.path.exists('test_calculator.db'):
        os.remove('test_calculator.db')
    
    # Override DB name for testing
    database.DB_NAME = 'test_calculator.db'
    database.init_db()
    
    yield
    
    if os.path.exists('test_calculator.db'):
        os.remove('test_calculator.db')

client = TestClient(app)

# --- Unit Tests for math_lib ---
def test_math_add():
    assert math_lib.add(2, 3) == 5

def test_math_subtract():
    assert math_lib.subtract(5, 3) == 2

def test_math_multiply():
    assert math_lib.multiply(4, 3) == 12

def test_math_divide():
    assert math_lib.divide(10, 2) == 5
    with pytest.raises(ValueError):
        math_lib.divide(10, 0)

# --- Integration Tests for API ---
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Online Math Calculator" in response.text

def test_calculate_success():
    response = client.post("/api/v1/calculate", json={
        "operation": "add",
        "operand_a": 10.5,
        "operand_b": 5.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["result"] == 15.5

def test_calculate_invalid_operation():
    response = client.post("/api/v1/calculate", json={
        "operation": "power",
        "operand_a": 10.5,
        "operand_b": 5.0
    })
    assert response.status_code == 400

def test_calculate_divide_by_zero():
    response = client.post("/api/v1/calculate", json={
        "operation": "divide",
        "operand_a": 10.5,
        "operand_b": 0.0
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Division by zero"

def test_history():
    # Insert some calculations
    client.post("/api/v1/calculate", json={"operation": "add", "operand_a": 1, "operand_b": 2})
    client.post("/api/v1/calculate", json={"operation": "multiply", "operand_a": 3, "operand_b": 4})
    
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    history = data["data"]
    assert len(history) == 2
    # The last inserted should be first because of ORDER BY id DESC
    assert history[0]["operation"] == "multiply"
    assert history[0]["result"] == 12.0
    assert history[1]["operation"] == "add"
    assert history[1]["result"] == 3.0
