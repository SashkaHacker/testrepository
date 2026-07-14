from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(tags=["auth"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> models.User:
    username = data.username.strip()
    email = data.email.lower().strip()
    existing_user = db.scalar(
        select(models.User).where(
            or_(models.User.username == username, models.User.email == email)
        )
    )
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = models.User(
        username=username,
        email=email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.Token:
    user = db.scalar(
        select(models.User).where(models.User.username == form_data.username.strip())
    )
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=create_access_token({"sub": user.username}))
