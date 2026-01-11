from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/login/google")
async def google_login(token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    # 1. SIMULATION BYPASS: If token is 'TEST_TOKEN', use mock data
    if token == "TEST_TOKEN":
        user_data = {
            "email": "testuser@example.com",
            "full_name": "Test Citizen",
            "google_id": "123456789",
        }
    else:
        # 2. REAL VERIFICATION: Only runs for real JWTs
        user_data = auth_service.verify_google_token(token)
        if not user_data:
            raise HTTPException(status_code=400, detail="Invalid Google Token")

    # 3. Standard User Fetch/Create Logic
    result = await db.execute(select(User).filter(User.email == user_data['email']))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=user_data['email'],
            full_name=user_data['full_name'],
            google_id=user_data['google_id'],
            role=UserRole.CITIZEN,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = auth_service.create_access_token(data={"sub": user.email})

    # Return structure matching what your AuthContext expects
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "department_id": user.department_id  # Add this line
        }
    }