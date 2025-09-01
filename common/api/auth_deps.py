# common/api/auth_deps.py
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from common.db.session import get_db
from common.models.user import User
from common.models.session_token import SessionToken
from services.auth_service.utils.security import verify_access_token

# в Swagger отдельный “замок”
bearer_scheme_user = HTTPBearer(auto_error=False, scheme_name="UserAuth")

def _assert_session_alive(db: Session, jti: str):
    s = db.query(SessionToken).filter(SessionToken.jti == jti).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.is_revoked:
        raise HTTPException(status_code=403, detail="Session revoked")
    if s.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    return s

def _verify_token_and_session(token: str, db: Session) -> dict:
    try:
        payload = verify_access_token(token)
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(status_code=401, detail="Token missing jti")
        sess = _assert_session_alive(db, jti)
        sub = payload.get("sub")
        user_id = int(sub)
        if sess.user_id != user_id:
            raise HTTPException(status_code=401, detail="Session does not belong to user")
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

def _extract_bearer(credentials: HTTPAuthorizationCredentials | None) -> str:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return credentials.credentials

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme_user),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer(credentials)
    payload = _verify_token_and_session(token, db)
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return user

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme_user),
    db: Session = Depends(get_db),
) -> int:
    token = _extract_bearer(credentials)
    payload = _verify_token_and_session(token, db)
    return int(payload["sub"])
