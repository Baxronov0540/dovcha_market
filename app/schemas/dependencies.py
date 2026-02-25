from fastapi import HTTPException, Depends
from sqlalchemy import select
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from datetime import datetime, timezone
from app.database import db_dep
from app.models import User
from app.utils import decode_jwt_token

jwt_security = HTTPBearer(auto_error=False)

credentials_dep = Annotated[HTTPAuthorizationCredentials, Depends(jwt_security)]


def get_current_user_jwt(session: db_dep, credintilas: credentials_dep):

    if not credintilas:
        raise HTTPException(status_code=401, detail="Invalid credintials")
    decode_data = decode_jwt_token(credintilas.credentials)
    user_id, exp = decode_data["user_id"], datetime.fromtimestamp(decode_data["exp"])

    if exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired!")

    stmt = select(User).where(User.id == user_id)
    user = session.execute(statement=stmt).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return User


current_user_jwt_dep = Annotated[User, Depends(get_current_user_jwt)]
