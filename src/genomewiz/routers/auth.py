from fastapi import APIRouter, Request, Depends
from starlette.responses import JSONResponse
from genomewiz.core.auth import login, auth_callback, get_current_user
from genomewiz.db.base import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def auth_login(request: Request):
    return await login(request)

@router.get("/callback")
async def auth_cb(request: Request, db: Session = Depends(get_db)):
    return await auth_callback(request, db)

@router.get("/logout")
def auth_logout(request: Request):
    request.session.clear()
    return JSONResponse({"ok": True})

@router.get("/me")
def whoami(user=Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"], "roles": user["roles"]}
