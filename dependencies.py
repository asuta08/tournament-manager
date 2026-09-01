from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from exceptions import AuthError
from security import decode_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise AuthError("Invalid token!", 401)

    user_id = payload.get("sub")
    if not user_id:
        raise AuthError("Invalid token payload!", 401)

    return int(user_id)
