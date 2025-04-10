# I want to create a service that will authenticate a user based on a JWT token

from fastapi import HTTPException
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import os


class AuthenticationService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = algorithm

    def authenticate(self, token: str) -> Optional[dict]:
        try:
            # Verify the token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Return the payload if valid
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error authenticating: {str(e)}")
    