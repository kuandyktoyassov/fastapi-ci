from pydantic import BaseModel


class RecipeCreate(BaseModel):
    title: str
    cooking_time: int
    ingredients: str
    description: str


class RecipeResponse(BaseModel):
    id: int
    title: str
    cooking_time: int
    ingredients: str
    description: str
    views: int

    class Config:
        from_attributes = True
