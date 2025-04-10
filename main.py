from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import os
import tempfile
from services.upload.upload import UploadServiceFactory
from services.authentication.authenticate import AuthenticationService
from typing import Optional

# Initialize the services
upload_service = UploadServiceFactory.create()
auth_service = AuthenticationService(secret_key=os.getenv("JWT_SECRET"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(title="Spends App API", description="API for the Spends App")

# Create a security scheme
security = HTTPBearer()

# Define a dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current authenticated user.
    
    Args:
        credentials (HTTPAuthorizationCredentials): The authorization credentials
        
    Returns:
        dict: The user payload
        
    Raises:
        HTTPException: If the token is invalid
    """
    try:
        # Authenticate the token
        payload = auth_service.authenticate(credentials.credentials)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Upload a file to the storage service.
    
    Args:
        file (UploadFile): The file to upload
        current_user (dict): The current authenticated user
        
    Returns:
        dict: A message with the URL of the uploaded file
        
    Raises:
        HTTPException: If there's an error uploading the file
    """
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Upload the temporary file to S3
        url = upload_service.upload_file(temp_file_path, file.filename)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return {
            "message": "File uploaded successfully", 
            "url": url,
            "user": current_user
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")

@app.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get the current user's information.
    
    Args:
        current_user (dict): The current authenticated user
        
    Returns:
        dict: The user's information
    """
    return current_user
