from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

# === Initialize HTTP Bearer Security ===
security = HTTPBearer(auto_error=False)

# === Verify Bearer Token ===
def verify_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    # Allow OPTIONS requests (CORS preflight) to pass through
    if request.method == "OPTIONS":
        return
    
    # Check if credentials were provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    # === Check if provided token matches the expected API token ===
    if credentials.credentials != settings.API_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
