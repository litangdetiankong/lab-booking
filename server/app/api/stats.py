from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.response import ok
from app.db.database import get_db
from app.db.models import User
from app.services import stats_service

router = APIRouter()

@router.get("")
def stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ok(stats_service.get_stats(db, user.id, is_admin=(user.role == "admin")))