from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

security = HTTPBearer(auto_error=False)

def verify_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if request.method == "OPTIONS":
        return

    # If token is not set in env, disable auth (dev mode)
    if not getattr(settings, "API_BEARER_TOKEN", None):
        return

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if credentials.credentials != settings.API_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
