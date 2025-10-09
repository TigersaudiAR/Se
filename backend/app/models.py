from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserRead(UserBase):
    id: int


class UserCreate(UserBase):
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class ProductBase(SQLModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: int = 0
    image_url: Optional[str] = None


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductRead(ProductBase):
    id: int


class ProductCreate(ProductBase):
    pass


class OrderItemBase(SQLModel):
    product_id: int
    quantity: int = 1
    unit_price: float


class OrderBase(SQLModel):
    customer_name: str
    customer_phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "new"


class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderRead(OrderBase):
    id: int


class OrderItem(OrderItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    order: "Order" = Relationship(back_populates="items")


class OrderCreateItem(OrderItemBase):
    pass


class OrderCreate(OrderBase):
    items: List[OrderCreateItem]
