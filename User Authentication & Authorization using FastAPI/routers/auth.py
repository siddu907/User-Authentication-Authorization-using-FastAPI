from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

import crud
import models
import oauth2
import schemas
import utils
from config import settings
from database import get_db
from rate_limiter import limiter
from token_blacklist import blacklist_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def signup(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db), response: Response = None):
    existing_user = crud.get_user_by_email(db, str(user.email))
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    created_user = crud.create_user(db, user)
    verification_token = oauth2.create_email_verification_token(
        {"user_id": created_user.id, "email": str(created_user.email)}
    )
    tokens = oauth2.create_login_tokens(created_user, message="Signup successful")
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        samesite="lax",
        path="/",
        max_age=1800,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="lax",
        path="/",
        max_age=604800,
    )
    response.set_cookie(
        key="verification_token",
        value=verification_token,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=3600,
    )
    response_data = schemas.UserResponse.model_validate(created_user).model_dump()
    response_data["verification_token"] = verification_token
    response_data["message"] = "Signup successful"
    return response_data


@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login(request: Request, user_credentials: schemas.UserLogin, db: Session = Depends(get_db), response: Response = None):
    user = crud.get_user_by_email(db, str(user_credentials.email))
    if not user or not utils.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    tokens = oauth2.create_login_tokens(user, message="Login successful")
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        samesite="lax",
        path="/",
        max_age=1800,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="lax",
        path="/",
        max_age=604800,
    )
    return tokens


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user


@router.post("/refresh", response_model=schemas.Token)
@limiter.limit("10/minute")
def refresh_token(request: Request, db: Session = Depends(get_db), response: Response = None):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = oauth2.verify_refresh_token(refresh_token)
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tokens = oauth2.create_login_tokens(user)
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        samesite="lax",
        path="/",
        max_age=1800,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="lax",
        path="/",
        max_age=604800,
    )
    return tokens


@router.post("/verify-email")
@limiter.limit("10/minute")
def verify_email(request: Request, db: Session = Depends(get_db), response: Response = None):
    token = request.cookies.get("verification_token")

    if token is None:
        raise HTTPException(status_code=401, detail="Verification token not found")

    token_data = oauth2.verify_email_verification_token(token)
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if response is not None:
        response.delete_cookie("verification_token", path="/")

    return {"message": "Email verified successfully", "full_name": user.full_name}


@router.post("/forgot-password")
def forgot_password(payload: schemas.ForgotPassword, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, str(payload.email))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = oauth2.create_password_reset_token({"user_id": user.id, "email": str(user.email)})
    return {"message": "Password reset instructions sent", "reset_token": reset_token}


@router.post("/reset-password")
def reset_password(payload: schemas.ResetPassword, db: Session = Depends(get_db)):
    token_data = oauth2.verify_password_reset_token(payload.token)
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = utils.hash_password(payload.new_password)
    db.commit()
    return {"message": "Password reset successfully"}


@router.get("/admin")
def admin_dashboard(current_user: models.User = Depends(oauth2.get_current_admin)):
    return {"message": f"Welcome admin {current_user.full_name}"}
