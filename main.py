from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_db
from models import Recipe
from schemas import RecipeCreate, RecipeResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Cook Book API",
    description="API для кулинарной книги",
    version="1.0",
    lifespan=lifespan,
)


@app.post("/recipes", response_model=RecipeResponse)
async def create_recipe(recipe: RecipeCreate, db: AsyncSession = Depends(get_db)):
    new_recipe = Recipe(**recipe.dict())

    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)

    return new_recipe


@app.get("/recipes")
async def get_recipes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recipe).order_by(desc(Recipe.views), Recipe.cooking_time)
    )

    recipes = result.scalars().all()

    return [
        {
            "id": recipe.id,
            "title": recipe.title,
            "views": recipe.views,
            "cooking_time": recipe.cooking_time,
        }
        for recipe in recipes
    ]


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)

    return recipe
