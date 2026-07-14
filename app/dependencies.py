from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app import models
from app.database import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> models.User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if not isinstance(username, str):
            raise credentials_error
    except jwt.PyJWTError as error:
        raise credentials_error from error

    user = db.scalar(select(models.User).where(models.User.username == username))
    if user is None:
        raise credentials_error
    return user
