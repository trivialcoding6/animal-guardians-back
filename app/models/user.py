# models/user.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
   
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    name: str
    email: str = Field(unique=True, index=True)
    password: str