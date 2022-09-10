
from datetime import datetime
from typing import List
from pydantic import BaseModel


class ItemSchema(BaseModel):
    title: str
    price: float
    old_price: float = None
    image: str
    link: str
    shop: str
    category: str
    shop_item_id: int
    shop_id: int
    history: list
    weight: str = None
    update_time: datetime
    status: int

    class Config:
        orm_mode = True


class ItemsShema(BaseModel):
    items: List[ItemSchema]


