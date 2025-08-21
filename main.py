from fastapi import FastAPI, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import typing
from random import randrange
import psycopg2
from pydantic import BaseModel, Field

try:
    conn = psycopg2.connect(
        database = 'employee',
        user = 'postgres',
        password = '091004',
        host = 'localhost',
        port = '5432'
    ) 
    cursor = conn.cursor()
except Exception as error:
    print(error)   

app = FastAPI()



templates = Jinja2Templates(directory="templates")

try:
    class Employee(BaseModel):
        id: str = Field(..., title='Employee ID',pattern='^[A-Z0-9]{10}$',description=" ID should be exactly 10 chars")
        name: str = Field(..., min_length=3, max_length=50, pattern='^[a-zA-Z]+$', title='Full Name', description="Name dosnt conatin spaces")
        age: int = Field(..., gt=18, lt=100, description="Age must be between 19 and 99")
        department: str = Field(..., min_length=5, max_length=50, description="Department name length between 5 and 50 characters")
except Exception as error:
    print(error)

@app.get('/')
def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home Page", "user": "Alice"})


#CREATE EMPLOYEE
@app.post('/employess')
def add_employee(employee: Employee):
    try:
        cursor.execute('''SELECT * FROM emp_details WHERE id = %s''',(employee.id,))
        result = cursor.fetchone()
        if result:
           return {'Alert':'Employee Already exist'}
        else:
            cursor.execute('''
                INSERT INTO emp_details(id,name,age,Department) VALUES(%s,%s,%s,%s)''',
                (employee.id,employee.name,employee.age,employee.department))  
            conn.commit()
        return {'Result':'Employee Added','Data':employee}
    except Exception as error1:
        print(error1)


#READ EMPLOYEE
@app.get('/read')
def read_all_employee():
    try:
        cursor.execute('''SELECT * FROM emp_details''')
        result = cursor.fetchall()
        return {'Data Retrived':result}  
    except Exception as error:
        print(error)

@app.get('/read/{id}')
def read_employee(id:str = Path(...,regex='^[A-Z0-9]{10}$')):
    try:
        cursor.execute('''SELECT * FROM emp_details WHERE id = %s''',(id,))
        res = cursor.fetchone()
        if res:
            return {'Data Retrived':res}
            conn.commit()
        else:
            return 'EMPLOYEE NOT EXIST.....'   
    except Exception as error:
        print(error)  


#UPDATE EMPLOYEE
@app.put('/update/{id}')
def update_emp_details(employee: Employee, id:str = Path(...,regex='^[A-Z0-9]{10}$')):
    try:
        cursor.execute('''SELECT *FROM emp_details WHERE id = %s''',(id,))
        res = cursor.fetchone()
        if not res:
            return {'ALERT':'NO EMPLOYEE IS THERE WITH THIS ID\t{id}'}
        else:
            cursor.execute('''UPDATE emp_details SET name = %s, age = %s, Department = %s WHERE id = %s''',(employee.name, employee.age, employee.department, id))
            conn.commit()
            return {'Result':f'New Details updated {employee}'}
    except Exception as error:
        print(error)


#DELETE EMPLOYEE
@app.delete('/delete/{id}')
def delete_details(id:str = Path(...,regex='^[A-Z0-9]{10}$')):
    try:
        cursor.execute('''DELETE FROM emp_details WHERE id = %s''',(id,))
        conn.commit()
        return {'Result':f'ID:{id} IS REMOVED.......'}
    except Exception as error:
        print(error)
