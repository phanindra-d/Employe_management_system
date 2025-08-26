from pydantic import BaseModel, Field

try:
    class Employee(BaseModel):
        id: str = Field(..., title='Employee ID',pattern='^[A-Z0-9]{10}$')
        name: str = Field(..., min_length=3, max_length=50, pattern='^[a-zA-Z ]+$', title='Full Name')
        age: int = Field(..., gt=18, lt=100)
        department: str = Field(..., min_length=1, max_length=50)
    
    class EmployeeUpdate(BaseModel):
        name: str = Field(..., min_length=3, max_length=50, pattern='^[a-zA-Z\s]+$')
        age: int =  Field(..., gt=18, lt=100)
        department: str =  Field(..., min_length=1, max_length=50)  

except Exception as error:
    print(error)