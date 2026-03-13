from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.configurations.settings import settings
from src.services import SellerService

bearer_scheme = HTTPBearer()


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


async def get_current_seller(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        seller_id = payload.get("sub")
        if seller_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    seller = await SellerService(session).get_single_seller(int(seller_id))
    if seller is None:
        raise credentials_exception

    return seller