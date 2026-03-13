from pydantic import BaseModel, EmailStr


class TokenRequest(BaseModel):
    e_mail: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"