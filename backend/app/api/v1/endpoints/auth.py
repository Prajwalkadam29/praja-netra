from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import auth_service

router = APIRouter()

@router.post("/login/google")
async def google_login(token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    user_data = auth_service.verify_google_token(token)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid Google Token")

    result = await db.execute(select(User).filter(User.email == user_data['email']))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=user_data['email'],
            full_name=user_data['full_name'],
            google_id=user_data['google_id'],
            role=UserRole.CITIZEN
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}