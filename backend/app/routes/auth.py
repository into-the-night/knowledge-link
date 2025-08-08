from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from typing import Optional
import httpx
from datetime import datetime, timedelta
import jwt
import secrets

from app.config.config import settings
from app.utils.database import get_database
from app.routes.models import UserResponse, TokenResponse
from app.utils.session_store import session_store


router = APIRouter()


def generate_state_token() -> str:
    """Generate a secure random state token for OAuth."""
    return secrets.token_urlsafe(32)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request) -> Optional[dict]:
    """Get the current user from the session or token."""
    # Try to get user from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                db = get_database()
                user = await db["users"].find_one({"_id": user_id})
                if user:
                    user["id"] = user["_id"]
                    return user
        except jwt.JWTError:
            pass
    
    # Try to get user from session
    session_id = request.cookies.get("session_id")
    if session_id:
        user_data = await session_store.get(f"session_{session_id}")
        if user_data:
            return user_data
    
    return None


@router.get("/auth/google")
async def google_login():
    """Initiate Google OAuth login flow."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )
    
    state = generate_state_token()
    # Store state for verification with 10 minute expiration
    await session_store.set(f"state_{state}", True, expire_seconds=600)
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid email profile"
        f"&state={state}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    
    return RedirectResponse(url=google_auth_url)


@router.get("/auth/callback")
async def google_callback(code: str, state: str):
    """Handle Google OAuth callback."""
    # Verify state token
    state_valid = await session_store.exists(f"state_{state}")
    if not state_valid:
        raise HTTPException(status_code=400, detail="Invalid state token")
    
    # Clean up state token
    await session_store.delete(f"state_{state}")
    
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        tokens = token_response.json()
        
        # Get user info from Google
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        if user_info_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_info = user_info_response.json()
    
    # Save or update user in database
    db = get_database()
    user_data = {
        "_id": user_info["id"],
        "email": user_info["email"],
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "updated_at": datetime.utcnow()
    }
    
    # Upsert user
    await db["users"].update_one(
        {"_id": user_info["id"]},
        {"$set": user_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
        upsert=True
    )
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user_info["id"], "email": user_info["email"]}
    )
    
    # Create session
    session_id = secrets.token_urlsafe(32)
    await session_store.set(
        f"session_{session_id}",
        {
            "id": user_info["id"],
            "email": user_info["email"],
            "name": user_info.get("name"),
            "picture": user_info.get("picture")
        },
        expire_seconds=7 * 24 * 60 * 60  # 7 days
    )
    
    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_URL}?token={access_token}"
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return response


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return UserResponse(**current_user)


@router.post("/logout")
async def logout(request: Request):
    """Logout the current user."""
    # Remove session
    session_id = request.cookies.get("session_id")
    if session_id:
        await session_store.delete(f"session_{session_id}")
    
    response = {"message": "Successfully logged out"}
    return response
