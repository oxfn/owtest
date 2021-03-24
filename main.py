from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes.users import router as users_router

app = FastAPI()
app.include_router(users_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    """Index page."""
    return templates.TemplateResponse("index.html", {"request": request})
