import pytest
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta
import os
from services.authentication.authenticate import AuthenticationService

# Set up environment variable for testing
os.environ["JWT_SECRET_KEY"] = "test_secret_key"

@pytest.fixture
def auth_service():
    return AuthenticationService(secret_key="test_secret_key")

def test_authenticate_valid_token(auth_service):
    # Create a valid token
    payload = {
        "sub": "test_user",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, auth_service.secret_key, algorithm=auth_service.algorithm)
    
    # Test authentication
    result = auth_service.authenticate(token)
    
    # Verify the result
    assert result is not None
    assert result["sub"] == "test_user"

def test_authenticate_invalid_token(auth_service):
    # Create an invalid token with wrong secret key
    payload = {
        "sub": "test_user",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, "wrong_secret_key", algorithm=auth_service.algorithm)
    
    # Test authentication should raise an exception
    with pytest.raises(HTTPException) as excinfo:
        auth_service.authenticate(token)
    
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token"

def test_authenticate_expired_token(auth_service):
    # Create an expired token
    payload = {
        "sub": "test_user",
        "exp": datetime.utcnow() - timedelta(minutes=30)  # Expired 30 minutes ago
    }
    token = jwt.encode(payload, auth_service.secret_key, algorithm=auth_service.algorithm)
    
    # Test authentication should raise an exception
    with pytest.raises(HTTPException) as excinfo:
        auth_service.authenticate(token)
    
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token"

def test_authenticate_malformed_token(auth_service):
    # Test with a malformed token
    malformed_token = "not.a.valid.token"
    
    # Test authentication should raise an exception
    with pytest.raises(HTTPException) as excinfo:
        auth_service.authenticate(malformed_token)
    
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token" 