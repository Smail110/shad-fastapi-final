from pydantic import BaseModel, EmailStr

from .books import ReturnedBook


class SellerBase(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


class IncomingSeller(SellerBase):
    password: str


class UpdateSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


class ReturnedSeller(SellerBase):
    id: int

    model_config = {"from_attributes": True}


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook] = []

    model_config = {"from_attributes": True}


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]