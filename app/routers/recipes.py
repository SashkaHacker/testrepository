from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user


router = APIRouter(prefix="/recipes", tags=["recipes"])


def get_owned_recipe_or_404(
    recipe_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> models.Recipe:
    """Return a recipe only when it belongs to the authenticated user."""
    recipe = db.get(models.Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No access to this recipe")
    return recipe


@router.get("", response_model=list[schemas.RecipeResponse])
def get_recipes(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[models.Recipe]:
    statement = select(models.Recipe).where(
        models.Recipe.owner_id == current_user.id
    )
    return list(db.scalars(statement).all())


@router.post("", response_model=schemas.RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    data: schemas.RecipeCreate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> models.Recipe:
    recipe = models.Recipe(**data.model_dump(), owner_id=current_user.id)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.get("/{recipe_id}", response_model=schemas.RecipeResponse)
def get_recipe(
    recipe: Annotated[models.Recipe, Depends(get_owned_recipe_or_404)],
) -> models.Recipe:
    return recipe


@router.patch("/{recipe_id}", response_model=schemas.RecipeResponse)
def update_recipe(
    data: schemas.RecipeUpdate,
    recipe: Annotated[models.Recipe, Depends(get_owned_recipe_or_404)],
    db: Annotated[Session, Depends(get_db)],
) -> models.Recipe:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(recipe, field, value)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe: Annotated[models.Recipe, Depends(get_owned_recipe_or_404)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    db.delete(recipe)
    db.commit()
