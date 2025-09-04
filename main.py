from fastapi import FastAPI, Path, Request, status, Form, HTTPException, Depends, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import typing 
from random import randrange
import psycopg2
from dotenv import load_dotenv
import os
from models import Employee, EmployeeUpdate
from utils import get_hashed_password, verify_password
from token_utils import create_access_token, create_refresh_token, verify_refresh_token, verify_token
from fastapi.security import HTTPBearer
import logging

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

load_dotenv()

API_URL = os.getenv("API_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    conn = psycopg2.connect(
        database =os.getenv('DB_NAME'),
        user = os.getenv('USER_NAME'),
        password = os.getenv('DB_PASSCODE'),
        host = os.getenv('DB_HOST'),
        port = os.getenv('DB_PORT')
    ) 
    cursor = conn.cursor()
    print('Connected success')
except Exception as error:
    print(error)   



@app.get("/")
def dashboard_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        token = request.cookies.get("access_token")
        
        if not token:
            logger.warning("No access token found")
            return RedirectResponse(url="/login", status_code=303)
        
        try:
            user_id = verify_token(token)
            logger.info(f"User authenticated: {user_id}")
            return templates.TemplateResponse("dashboard.html", {"request": request})
        except:
            logger.warning("Invalid token")
            return RedirectResponse(url="/login", status_code=303)
            
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return RedirectResponse(url="/login", status_code=303)
    

@app.post("/signup")
async def signup(username: str = Form(...), full_name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        cursor.execute("SELECT * FROM user_table WHERE user_name = %s", (username,))
        if cursor.fetchone():
            return {"error": "Username already exists"}
        
        # Here password is hashed before storing
        hashed_password = get_hashed_password(password=password)
        cursor.execute(
            "INSERT INTO user_table (user_name, full_name, email, password) VALUES (%s, %s, %s, %s)",
            (username, full_name, email, hashed_password)
        )
        conn.commit()
        return RedirectResponse(url="/login", status_code=303)
        
    except Exception as error:
        print(error)
        return {"error": "Signup failed"}



@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    try:
        logger.info(f"Login attempt for user: {username}")
        
        cursor.execute(
            "SELECT user_id, user_name, password FROM user_table WHERE user_name = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user or not verify_password(password, user[2]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create token
        access_token = create_access_token(str(user[0]))
        
        # Create response with redirect
        response = RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_303_SEE_OTHER
        )
        
        # Set cookie in the redirect response
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=1800,
            samesite="lax"
        )
        
        return response
            
    except Exception as error:
        logger.error(f"Login error: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(error)}"
        )

@app.post("/refresh")
async def refresh_token(refresh_token: str):
    user_id = verify_refresh_token(refresh_token)
    new_access_token = create_access_token(user_id)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

security = HTTPBearer()

@app.post("/employess")
async def add_employee(employee: Employee):
    try:
        # Log the received data
        print(f"Received data: {employee.model_dump() if hasattr(employee, 'model_dump') else employee.dict()}")
        
        # Check if employee exists
        cursor.execute("SELECT id FROM emp_details WHERE id = %s", (employee.id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Employee already exists")
        
        # Insert employee
        cursor.execute(
            "INSERT INTO emp_details (id, name, age, department) VALUES (%s, %s, %s, %s)",
            (employee.id, employee.name, employee.age, employee.department)
        )
        conn.commit()
        print("Employee added successfully")
        
        return {"message": "Success"}
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as is
        print(f"HTTP Exception: {he.detail}")
        raise
        
    except Exception as e:
        # Log the actual exception
        error_msg = str(e)
        print(f"Database error: {error_msg}")
        conn.rollback()
        
        # Return a proper error message
        raise HTTPException(
            status_code=500, 
            detail=error_msg
        )

#READ EMPLOYEE
@app.get('/read')
async def read_all_employee():  # Remove token dependency temporarily
    try:
        cursor.execute("SELECT id, name, age, department FROM emp_details")
        result = cursor.fetchall()
        
        # Convert result to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        result_list = []
        for row in result:
            result_list.append(dict(zip(columns, row)))
            
        return {"Result": result_list}
    except Exception as e:
        print(f"Error reading employees: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/read1/{id}')
async def read_employee(id: str):
    try:
        # Log the request
        print(f"Searching for employee with ID: {id}")
        
        # Validate ID format manually instead of using Path validation
        import re
        if not re.match(r'^ASP\d{7}$', id):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid ID format. Must be ASP followed by 7 digits."}
            )
        
        # Execute the query
        cursor.execute("SELECT id, name, age, department FROM emp_details WHERE id = %s", (id,))
        result = cursor.fetchall()
        
        # Convert result to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        result_list = []
        for row in result:
            result_list.append(dict(zip(columns, row)))
            
        # Log the result
        print(f"Search result: {result_list}")
            
        if not result_list:
            # Employee not found
            print(f"Employee with ID {id} not found")
            return JSONResponse(
                status_code=404,
                content={"detail": f"Employee with ID {id} not found"}
            )
            
        # Return successful result
        return {"Result": result_list}
        
    except Exception as e:
        # Log the error
        print(f"Error in read_employee: {str(e)}")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )



#UPDATE EMPLOYEE
@app.put('/update/{id}')
async def update_emp_details(employee: EmployeeUpdate, id: str = Path(..., regex='^ASP\d{7}$')):
    try:
        # Check if employee exists
        cursor.execute("SELECT id FROM emp_details WHERE id = %s", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Employee with ID {id} not found")
        
        # Update employee
        cursor.execute(
            "UPDATE emp_details SET name = %s, age = %s, department = %s WHERE id = %s",
            (employee.name, employee.age, employee.department, id)
        )
        conn.commit()
        
        # Return success response
        return {"Result": "Employee updated successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


#DELETE EMPLOYEE
@app.delete('/delete/{id}')
async def delete_details(id: str):  # Remove token dependency
    try:
        # Manual validation
        import re
        if not re.match(r'^ASP\d{7}$', id):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid ID format. Must be ASP followed by 7 digits."}
            )
            
        # Check if employee exists
        cursor.execute("SELECT id FROM emp_details WHERE id = %s", (id,))
        if not cursor.fetchone():
            return JSONResponse(
                status_code=404,
                content={"detail": f"Employee with ID {id} not found"}
            )
        
        # Delete employee
        cursor.execute("DELETE FROM emp_details WHERE id = %s", (id,))
        conn.commit()
        
        # Return success response
        return {"message": "Success"}
        
    except Exception as e:
        # Log and return error
        print(f"Error deleting employee: {str(e)}")
        conn.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

#Delete All Data
@app.delete('/delete_all/{flag}')
async def delete_all(
    flag: bool,
    token: str = Depends(verify_token)
):
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
