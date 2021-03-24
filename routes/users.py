from fastapi.routing import APIRouter

from models.users import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def profile():
    """Current user profile."""
    return {}


@router.post("/register")
async def register(user: User):
    """Register new user."""
    return user


@router.post("/login")
async def login(user: User):
    """Authenticate user."""
    return user
