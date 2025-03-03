from pydantic import BaseModel

class BuySneakers(BaseModel):
    sneaker_id: list[int]
    size: list[int]
    phone_number: str
    adress: str
    full_name: str
    payment: str