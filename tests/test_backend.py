import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Mom Voice ChatBot Backend is Running"}

def test_setup_pin():
    response = client.post("/api/auth/pin/setup", params={"pin": "1234"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_chat_text():
    response = client.post("/api/chat/text", params={"message": "안녕 엄마"})
    assert response.status_code == 200
    assert "reply" in response.json()
