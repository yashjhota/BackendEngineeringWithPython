from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from typing import List
from auth.hashing import hash_password
from auth.dependencies import get_current_user
from cache import get_cache, set_cache, delete_cache
from auth.rate_limiter import rate_limit
from fastapi import BackgroundTasks
from utils.tasks import send_welcome_email, log_user_action
from utils.logger import logger

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        logger.warning(f"Duplicate email attempt: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),  # ← hashed now
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user created: {new_user.id} - {new_user.email}")

    # these run AFTER response is sent
    background_tasks.add_task(send_welcome_email, new_user.email, new_user.name)
    background_tasks.add_task(log_user_action, new_user.id, "register")

    return new_user


@router.get("/", response_model=List[UserResponse])
def get_all_users(
    request: Request, db: Session = Depends(get_db), _: None = Depends(rate_limit)
):
    return db.query(User).all()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    # 1. check cache first
    cached = get_cache(f"user:{user_id}")
    if cached:
        print("Cache hit!")
        return cached

    # 2. cache miss — hit database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. store in cache for next time
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }
    set_cache(f"user:{user_id}", user_data)
    print("Cache miss — stored in Redis")

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updates: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if updates.name:
        user.name = updates.name
    if updates.email:
        user.email = updates.email
    db.commit()
    db.refresh(user)

    # invalidate cache — data changed
    delete_cache(f"user:{user_id}")

    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

    # invalidate cache — user gone
    delete_cache(f"user:{user_id}")
