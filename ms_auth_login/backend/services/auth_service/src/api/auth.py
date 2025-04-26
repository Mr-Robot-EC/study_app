from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import uuid4
import httpx
import jwt

from ..core.config import settings
from ..core.security import verify_password, get_password_hash, create_jwt_token
from ..db.session import get_db
from ..db.models import User, RefreshToken
from ..schemas import UserCreate, Token, RefreshTokenRequest, User as UserSchema
from .webhooks import trigger_webhook

router = APIRouter(tags=["authentication"])


@router.post("/register", response_model=UserSchema)
async def register_user(
        user_data: UserCreate,
        request: Request,
        db: Session = Depends(get_db)
):
    """Register a new user with email and password"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        id=uuid4(),
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        roles=["user"],
        permissions=["read:own"],
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Trigger webhook for user.created event
    await trigger_webhook(db, "user.created", new_user.id)

    # Return user data
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        request: Request = None,
        db: Session = Depends(get_db)
):
    """Generate access and refresh tokens"""
    # Authenticate user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # Define audiences (services that can use this token)
    audiences = ["pdf-service", "flashcard-service", "chat-service"]

    # Create access token
    access_token = create_jwt_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "name": user.full_name,
            "roles": user.roles,
            "permissions": user.permissions,
            "metadata": {
                "last_login": user.last_login.isoformat(),
                "login_method": "credentials"
            }
        },
        expires_delta=access_token_expires,
        audiences=audiences
    )

    # Create refresh token
    refresh_token = create_jwt_token(
        data={
            "sub": str(user.id),
            "token_type": "refresh",
        },
        expires_delta=refresh_token_expires
    )

    # Store refresh token in DB
    client_ip = request.client.host if request else None
    user_agent = request.headers.get("User-Agent") if request else None

    db_refresh = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + refresh_token_expires,
        client_ip=client_ip,
        user_agent=user_agent
    )
    db.add(db_refresh)
    db.commit()

    # Trigger webhook for user.login event
    await trigger_webhook(db, "user.login", user.id)

    # Return token response
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/token/refresh", response_model=Token)
async def refresh_token(
        refresh_data: RefreshTokenRequest,
        request: Request = None,
        db: Session = Depends(get_db)
):
    """Refresh access token using a refresh token"""
    try:
        # Decode refresh token without verification (to get the user ID)
        payload = jwt.decode(
            refresh_data.refresh_token,
            options={"verify_signature": False}
        )

        # Verify it's a refresh token
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify the token in database
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_data.refresh_token,
            RefreshToken.revoked_at == None
        ).first()

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check token expiration
        if db_token.expires_at < datetime.utcnow():
            # Revoke expired token
            db_token.revoked_at = datetime.utcnow()
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get associated user
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # Define audiences
        audiences = ["pdf-service", "flashcard-service", "chat-service"]

        # Create new access token
        access_token = create_jwt_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "roles": user.roles,
                "permissions": user.permissions,
                "metadata": {
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "login_method": "refresh"
                }
            },
            expires_delta=access_token_expires,
            audiences=audiences
        )

        # Create new refresh token
        new_refresh_token = create_jwt_token(
            data={
                "sub": str(user.id),
                "token_type": "refresh",
            },
            expires_delta=refresh_token_expires
        )

        # Revoke old token and store new one
        db_token.revoked_at = datetime.utcnow()

        # Client information
        client_ip = request.client.host if request else None
        user_agent = request.headers.get("User-Agent") if request else None

        # Create new token record
        new_db_token = RefreshToken(
            token=new_refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + refresh_token_expires,
            client_ip=client_ip,
            user_agent=user_agent
        )

        db.add(new_db_token)
        db.commit()

        # Trigger webhook for token.refresh event
        await trigger_webhook(db, "token.refresh", user.id)

        # Return token response
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
        refresh_data: LogoutRequest,
        request: Request = None,
        db: Session = Depends(get_db)
):
    """Revoke a refresh token (logout)"""
    if not refresh_data.refresh_token:
        return {"status": "success", "message": "No token provided"}

    # Find token in database
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_data.refresh_token,
        RefreshToken.revoked_at == None
    ).first()

    if db_token:
        # Revoke token
        db_token.revoked_at = datetime.utcnow()
        db.commit()

    return {"status": "success", "message": "Logout successful"}


@router.get("/login/google")
async def login_google(request: Request):
    """Redirect to Google OAuth login"""
    from authlib.integrations.starlette_client import OAuth

    # Initialize OAuth with Google provider
    oauth = OAuth()
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        client_kwargs={
            "scope": "openid email profile",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI
        }
    )

    # Create the redirect URL to Google login
    redirect_uri = request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    from authlib.integrations.starlette_client import OAuth
    from authlib.integrations.base_client import OAuthError

    # Initialize OAuth with Google provider
    oauth = OAuth()
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        client_kwargs={
            "scope": "openid email profile",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI
        }
    )

    try:
        # Get token and user info from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info or not user_info.get("email"):
            return {"error": "Could not fetch user information"}

        # Check if user exists by Google ID or email
        user = db.query(User).filter(
            (User.google_id == user_info.get("sub")) |
            (User.email == user_info.get("email"))
        ).first()

        if not user:
            # Create new user from Google profile
            user = User(
                id=uuid4(),
                email=user_info.get("email"),
                full_name=user_info.get("name", ""),
                google_id=user_info.get("sub"),
                roles=["user"],
                permissions=["read:own"],
                metadata={
                    "google_profile": {
                        "picture": user_info.get("picture"),
                        "locale": user_info.get("locale")
                    }
                }
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Trigger webhook for user.created event
            await trigger_webhook(db, "user.created", user.id)
        else:
            # Update existing user
            if not user.google_id:
                user.google_id = user_info.get("sub")

            # Update profile data
            user.full_name = user_info.get("name", user.full_name)
            user.is_active = True

            # Update metadata
            if not user.metadata:
                user.metadata = {}

            user.metadata.update({
                "google_profile": {
                    "picture": user_info.get("picture"),
                    "locale": user_info.get("locale")
                }
            })

            db.commit()

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # Define audiences
        audiences = ["pdf-service", "flashcard-service", "chat-service"]

        # Create access token
        access_token = create_jwt_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "roles": user.roles,
                "permissions": user.permissions,
                "metadata": {
                    "last_login": user.last_login.isoformat(),
                    "login_method": "google"
                }
            },
            expires_delta=access_token_expires,
            audiences=audiences
        )

        # Create refresh token
        refresh_token = create_jwt_token(
            data={
                "sub": str(user.id),
                "token_type": "refresh",
            },
            expires_delta=refresh_token_expires
        )

        # Store refresh token in DB
        client_ip = request.client.host if request else None
        user_agent = request.headers.get("User-Agent") if request else None

        db_refresh = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + refresh_token_expires,
            client_ip=client_ip,
            user_agent=user_agent
        )
        db.add(db_refresh)
        db.commit()

        # Trigger webhook for user.login event
        await trigger_webhook(db, "user.login", user.id)

        # Redirect to frontend with tokens
        # In production, use a better approach like a proper OAuth flow with state
        frontend_uri = "http://localhost:3000/auth/callback"
        redirect_url = f"{frontend_uri}?access_token={access_token}&refresh_token={refresh_token}"

        from starlette.responses import RedirectResponse
        return RedirectResponse(url=redirect_url)

    except OAuthError as error:
        return {"error": f"OAuth error: {error.error}"}