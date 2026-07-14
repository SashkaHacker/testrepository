from typing import Annotated

from fastapi import APIRouter, Depends

from app import models, schemas
from app.dependencies import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserResponse)
def read_current_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    return current_user
