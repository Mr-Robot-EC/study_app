from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from . import models, schemas, database

# Initialize FastAPI
app = FastAPI(title="Auth Service")

# Add middleware
app.add_middleware(SessionMiddleware, secret_key="YOUR_SESSION_SECRET")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup OAuth2
config = Config(".env")  # Load from environment variables
oauth = OAuth(config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id="GOOGLE_CLIENT_ID",
    client_secret="GOOGLE_CLIENT_SECRET",
    client_kwargs={
        "scope": "openid email profile",
        "redirect_uri": "YOUR_REDIRECT_URI"
    }
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT Settings
JWT_SECRET_KEY = "YOUR_JWT_SECRET_KEY"  # Change in production, load from env
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30


# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User Auth Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    import jwt
    from datetime import datetime, timedelta

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid4()),
        "iss": "auth.myservice.com"
    })

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# Helper functions for user operations
def create_user(db: Session, user_data: schemas.UserCreate):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        return None

    # Create new user
    db_user = models.User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        roles=["user"],  # Default role
        id=uuid4(),  # Generate UUID
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# Routes for Email/Password Auth
@app.post("/register", response_model=schemas.UserResponse)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user_data)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # Create JWT token
    access_token = create_jwt_token(
        data={
            "sub": str(db_user.id),
            "email": db_user.email,
            "name": db_user.full_name,
            "roles": db_user.roles,
            "aud": ["pdf-service", "flashcard-service", "chat-service"]
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Create refresh token
    refresh_token = create_jwt_token(
        data={
            "sub": str(db_user.id),
            "token_type": "refresh",
        },
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    # Store refresh token in DB (optional, for token revocation)
    db_refresh = models.RefreshToken(
        token=refresh_token,
        user_id=db_user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": db_user
    }


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token = create_jwt_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "name": user.full_name,
            "roles": user.roles,
            "aud": ["pdf-service", "flashcard-service", "chat-service"],
            "metadata": {
                "last_login": user.last_login.isoformat(),
                "login_method": "credentials"
            }
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_jwt_token(
        data={
            "sub": str(user.id),
            "token_type": "refresh",
        },
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    # Store refresh token in DB
    db_refresh = models.RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# Routes for Google OAuth
@app.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if user_info:
            # Check if user exists
            db_user = get_user_by_email(db, user_info["email"])

            if not db_user:
                # Create new user from Google profile
                db_user = models.User(
                    email=user_info["email"],
                    full_name=user_info.get("name", ""),
                    google_id=user_info.get("sub"),
                    roles=["user"],
                    id=uuid4()
                )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
            else:
                # Update Google ID if not already set
                if not db_user.google_id:
                    db_user.google_id = user_info.get("sub")
                    db.commit()

            # Update last login
            db_user.last_login = datetime.utcnow()
            db.commit()

            # Create tokens
            access_token = create_jwt_token(
                data={
                    "sub": str(db_user.id),
                    "email": db_user.email,
                    "name": db_user.full_name,
                    "roles": db_user.roles,
                    "aud": ["pdf-service", "flashcard-service", "chat-service"],
                    "metadata": {
                        "last_login": db_user.last_login.isoformat(),
                        "login_method": "google"
                    }
                },
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )

            refresh_token = create_jwt_token(
                data={
                    "sub": str(db_user.id),
                    "token_type": "refresh",
                },
                expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )

            # Store refresh token in DB
            db_refresh = models.RefreshToken(
                token=refresh_token,
                user_id=db_user.id,
                expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )
            db.add(db_refresh)
            db.commit()

            # Redirect to frontend with tokens (in production, use a better approach)
            frontend_uri = "YOUR_FRONTEND_URI"
            redirect_url = f"{frontend_uri}?access_token={access_token}&refresh_token={refresh_token}"
            return RedirectResponse(url=redirect_url)

        return JSONResponse({"error": "Could not fetch user information"})

    except OAuthError as error:
        return JSONResponse({"error": f"OAuth error: {error.error}"})


# Token refresh endpoint
@app.post("/token/refresh", response_model=schemas.Token)
async def refresh_token(
        refresh_data: schemas.RefreshTokenRequest,
        db: Session = Depends(get_db)
):
    import jwt
    from jwt.exceptions import PyJWTError

    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_data.refresh_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
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
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if token exists in DB (for revocation)
        db_token = db.query(models.RefreshToken).filter(
            models.RefreshToken.token == refresh_data.refresh_token,
            models.RefreshToken.revoked_at.is_(None)
        ).first()

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user
        user = get_user(db, UUID(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        new_access_token = create_jwt_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "roles": user.roles,
                "aud": ["pdf-service", "flashcard-service", "chat-service"],
                "metadata": {
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "login_method": "refresh"
                }
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # Optional: issue a new refresh token and invalidate the old one
        new_refresh_token = create_jwt_token(
            data={
                "sub": str(user.id),
                "token_type": "refresh",
            },
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        # Revoke old token and store new one
        db_token.revoked_at = datetime.utcnow()

        new_db_token = models.RefreshToken(
            token=new_refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        db.add(new_db_token)
        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# User management endpoints
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(
        current_user: models.User = Depends(get_current_user),
):
    return current_user


# Dependency for getting current user from token
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    import jwt
    from jwt.exceptions import PyJWTError

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Check if token is a refresh token (which shouldn't be used for auth)
        if payload.get("token_type") == "refresh":
            raise credentials_exception

        # Validate audience (optional)
        # if "aud" in payload and request_aud not in payload["aud"]:
        #    raise credentials_exception

    except PyJWTError:
        raise credentials_exception

    user = get_user(db, UUID(user_id))
    if user is None:
        raise credentials_exception

    return user


# Custom webhook triggers on user events
@app.post("/webhooks", response_model=schemas.WebhookResponse)
async def register_webhook(
        webhook: schemas.WebhookCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Only admin users can register webhooks
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to register webhooks"
        )

    db_webhook = models.Webhook(
        url=webhook.url,
        event_type=webhook.event_type,
        secret=webhook.secret,
        created_by=current_user.id
    )
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)

    return db_webhook


# Role management
@app.put("/users/{user_id}/roles", response_model=schemas.User)
async def update_user_roles(
        user_id: UUID,
        roles_update: schemas.RolesUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Only admin users can update roles
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update roles"
        )

    # Get user to update
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update roles
    user.roles = roles_update.roles
    db.commit()
    db.refresh(user)

    return user


# Token revocation (logout)
@app.post("/logout")
async def logout(
        token_data: schemas.LogoutRequest,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Revoke refresh token if provided
    if token_data.refresh_token:
        db_token = db.query(models.RefreshToken).filter(
            models.RefreshToken.token == token_data.refresh_token,
            models.RefreshToken.user_id == current_user.id,
            models.RefreshToken.revoked_at.is_(None)
        ).first()

        if db_token:
            db_token.revoked_at = datetime.utcnow()
            db.commit()

    return {"status": "success", "message": "Logout successful"}