from datetime import datetime
from datetime import timedelta
from datetime import UTC
from typing import Optional

from jose import JWTError
from jose import jwt

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from config import settings

from database import get_db

import models
import schemas
from token_blacklist import is_token_blacklisted

oauth2_scheme = OAuth2PasswordBearer(

    tokenUrl="/auth/login",

    auto_error=False

)

def create_token(data: dict, expires_delta: timedelta, token_type: str):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Create Access Token

def create_access_token(data: dict):

    """
    Create JWT Access Token.
    """

    return create_token(
        data,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


# Create Refresh Token

def create_refresh_token(data: dict):

    """
    Create JWT Refresh Token.
    """

    return create_token(
        data,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def create_email_verification_token(data: dict):
    return create_token(data, timedelta(days=1), "email_verification")


def create_password_reset_token(data: dict):
    return create_token(data, timedelta(hours=1), "password_reset")

# Verify Token

def verify_token(token: str):

    """
    Verify JWT Token.
    """

    credentials_exception = HTTPException(

        status_code=status.HTTP_401_UNAUTHORIZED,

        detail="Could not validate credentials",

        headers={"WWW-Authenticate": "Bearer"}

    )

    try:

        # Decode JWT Token
        payload = jwt.decode(

            token,

            settings.SECRET_KEY,

            algorithms=[settings.ALGORITHM]

        )

        # Extract values from payload
        user_id = payload.get("user_id")

        email = payload.get("email")

        role = payload.get("role")

        token_type = payload.get("type")

        # Check whether required fields exist
        if user_id is None:

            raise credentials_exception

        # Store extracted data inside TokenData schema
        token_data = schemas.TokenData(

            user_id=user_id,

            email=email,

            role=role

        )

        return token_data, token_type

    except JWTError:

        raise credentials_exception


# Get Current User

def get_current_user(

    request: Request,

    token: Optional[str] = Depends(oauth2_scheme),

    db: Session = Depends(get_db)

):

    """
    Return currently logged-in user.
    """

    cookie_token = request.cookies.get("access_token")

    token = token or cookie_token

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return get_user_from_token(token, db)


def get_user_from_token(token: str, db: Session):
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been blacklisted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    token_data, token_type = verify_token(token)

    # Only Access Token is allowed
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Access Token",
        )

    # Fetch user from database
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()

    # User not found
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

# Verify Refresh Token

def verify_refresh_token(token: str):

    """
    Verify Refresh Token.
    """

    token_data, token_type = verify_token(token)

    if token_type != "refresh":

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Invalid Refresh Token"

        )

    return token_data


def verify_email_verification_token(token: str):
    token_data, token_type = verify_token(token)
    if token_type != "email_verification":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email verification token",
        )
    return token_data


def verify_password_reset_token(token: str):
    token_data, token_type = verify_token(token)
    if token_type != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password reset token",
        )
    return token_data

# Get Current Admin

def get_current_admin(

    current_user: models.User = Depends(get_current_user)

):

    """
    Allow only Admin users.
    """

    if str(current_user.email).lower() != str(settings.ADMIN_EMAIL).lower():

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="You are not admin"

        )

    return current_user


def get_current_basic_user(

    current_user: models.User = Depends(get_current_user)

):

    """
    Allow only normal User accounts.
    """

    if str(current_user.email).lower() == str(settings.ADMIN_EMAIL).lower():

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="You are not user"

        )

    return current_user

# Create Login Tokens

def create_login_tokens(user: models.User, message: Optional[str] = None):

    """
    Generate both Access and Refresh Tokens.
    """

    payload = {

        "user_id": user.id,

        "email": user.email,

        "role": "Admin" if str(user.email).lower() == str(settings.ADMIN_EMAIL).lower() else "User"

    }

    access_token = create_access_token(payload)

    refresh_token = create_refresh_token(payload)

    token_data = {

        "access_token": access_token,

        "refresh_token": refresh_token,

        "token_type": "bearer"

    }

    if message is not None:
        token_data["message"] = message

    return token_data