# services/auth_service/deps/auth.py
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from services.auth_service.utils.security import verify_access_token
from common.db.session import get_db
from sqlalchemy.orm import Session
from common.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = credentials.credentials
    try:
        payload = verify_access_token(token)
        user_id = int(payload["sub"])
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Користувача не знайдено")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
