from pydantic import BaseModel, Field, EmailStr
from typing import Annotated

class Employee(BaseModel):
    id: str = Field(..., pattern=r'^ASP\d{7}$')
    name: str = Field(..., min_length=2)
    age: int = Field(..., gt=18, lt=100)
    department: str = Field(..., min_length=2)

class EmployeeUpdate(BaseModel):
    name: str = Field(..., min_length=2)
    age: int = Field(..., gt=18, lt=100)
    department: str = Field(..., min_length=2)

class UserCreate(BaseModel):
    username: str
    fullname: str
    email: EmailStr
    password: str