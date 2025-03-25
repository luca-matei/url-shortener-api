from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from v1.config import settings
from v1.schemas import User

security = HTTPBearer()


async def get_current_user(
    token: HTTPAuthorizationCredentials = Security(security),
) -> User:
    """Basic authentication"""
    if token:
        if token.credentials == settings.admin_token:
            return User(username="admin")
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authentication credentials"
            )
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
