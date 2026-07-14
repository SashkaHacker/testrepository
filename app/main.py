from fastapi import FastAPI

from app.routers import auth, recipes, users


app = FastAPI(title="Recipe Manager API — lesson 16 complete")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recipes.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
