from fastapi import FastAPI, Path, Request,status
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




try:
    class Employee(BaseModel):
        id: str = Field(..., title='Employee ID',pattern='^[A-Z0-9]{10}$')
        name: str = Field(..., min_length=3, max_length=50, pattern='^[a-zA-Z ]+$', title='Full Name')
        age: int = Field(..., gt=18, lt=100)
        department: str = Field(..., min_length=1, max_length=50)
    
    class EmployeeUpdate(BaseModel):
        name: str = Field(..., min_length=3, max_length=50, pattern='^[a-zA-Z ]+$')
        age: int =  Field(..., gt=18, lt=100)
        department: str =  Field(..., min_length=1, max_length=50)  

except Exception as error:
    print(error)

@app.get('/')
def home_page(request: Request):
    return "Welcome to student management system"


#CREATE EMPLOYEE
@app.post('/employess')
async def add_employee(employee: Employee, status_code=status.HTTP_201_CREATED):
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
        return employee
    except Exception as error1:
        print(error1)


#READ EMPLOYEE
@app.get('/read')
def read_all_employee():
    try:
        cursor.execute('''SELECT * FROM emp_details''')
        result = cursor.fetchall()
        return result
    except Exception as error:
        print(error)


@app.get('/read1/{id}')
def read_employee(id: str = Path(..., regex='^[A-Z0-9]{10}$')):
    try:
        cursor.execute('''SELECT * FROM emp_details WHERE id = %s''', (id,))
        res = cursor.fetchone()  
        if res:
            return {
                "id": res[0],
                "name": res[1],
                "age": res[2],
                "department": res[3]
            }
        else:
            return {"ALERT": f"No employee found with ID {id}"}
    except Exception as error:
        return {"error": str(error)}



#UPDATE EMPLOYEE
@app.put('/update/{id}')
def update_emp_details(employee: EmployeeUpdate, id:str = Path(...,regex='^[A-Z0-9]{10}$')):
    try:
        cursor.execute('''SELECT *FROM emp_details WHERE id = %s''',(id,))
        res = cursor.fetchone()
        if not res:
            return {'ALERT':'NO EMPLOYEE IS THERE WITH THIS ID\t{id}'}
        else:
            cursor.execute('''UPDATE emp_details SET name = %s, age = %s, Department = %s WHERE id = %s''',(employee.name, employee.age, employee.department, id))
            conn.commit()
            return employee
    except Exception as error:
        print(error)


#DELETE EMPLOYEE
@app.delete('/delete/{id}')
def delete_details(id:str = Path(...,regex='^[A-Z0-9]{10}$')):
    try:
        cursor.execute('''DELETE FROM emp_details WHERE id = %s''',(id,))
        conn.commit()
        return id
    except Exception as error:
        print(error)

#Delete All Data
@app.delete('/delete_all/{flag}')
def delete_all(flag:bool):
    try:
        cursor.execute('BEGIN;')
        cursor.execute('DELETE FROM emp_details;')
        if flag:
            conn.rollback()
        else:
            conn.commit()    
    except Exception as e:
        print(e)
        conn.rollback()
   