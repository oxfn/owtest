from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes.items import router as items_router
from .routes.users import router as users_router

app = FastAPI()

app.include_router(items_router)
app.include_router(users_router)

app.mount("/static", StaticFiles(directory="./app/static"), name="static")

templates = Jinja2Templates(directory="./app/templates")


@app.get("/")
async def index(request: Request):
    """Index page."""
    return templates.TemplateResponse("index.html", {"request": request})
