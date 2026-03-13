from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import create_access_token
from src.configurations.database import get_async_session
from src.schemas import TokenRequest, TokenResponse
from src.services import SellerService

token_router = APIRouter(prefix="/token", tags=["token"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@token_router.post("/", response_model=TokenResponse)
async def login_for_access_token(data: TokenRequest, session: DBSession):
    seller = await SellerService(session).get_by_email(data.e_mail)

    if seller is None or seller.password != data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect e_mail or password",
        )

    access_token = create_access_token({"sub": str(seller.id)})
    return {"access_token": access_token, "token_type": "bearer"}