from fastapi import HTTPException, status, Security, FastAPI
from fastapi.security import APIKeyHeader
import apikeys


api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in apikeys.API_KEYS:
        return api_key_header
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API Key")
