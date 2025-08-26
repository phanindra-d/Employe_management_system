import streamlit as st
import pandas as pd
import requests, re
import re
from dotenv import load_dotenv
import os 

load_dotenv()

API_URL = os.getenv("API_URL")


id_match = r"^[A-Z0-9]{10}$"
name_match = r"^[a-zA-Z\s]+$"

def view_details():
    try:
        st.subheader("Employee List")
        response = requests.get(f"{API_URL}/read")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data["Result"], columns=["Employee ID","Name","Age","Department"])
            df.insert(0, "Serial No", range(1, len(df) + 1))
            st.dataframe(df.set_index("Serial No"))
            st.divider()    
            st.success(f"Total Employes\t:{len(df)}")
            st.divider()
        else:
            st.error('Not Retrived')    
    except Exception as error:
        st.write(error)
            
          
        
        # DataFrame.insert(loc, column, value, allow_duplicates=False)
       

def add_details():
    try:
        st.subheader("Add New Employee")
        with st.form("add_employee_form"):
            id = st.text_input("Employee ID", max_chars=10, help="Length must be 10")
            name = st.text_input("Name", placeholder="No speacial char allowed")
            age = st.number_input("Age", placeholder="Age must be greater than 18",  min_value=19, max_value=70)
            department = st.selectbox("Department", ["AI&WEB ", "Testing", "HR", "SalesForce"])
            submitted = st.form_submit_button("Add Employee")
            if name and id:
                if not re.match(name_match, name) or not re.match(id_match, id):
                    st.error("Invalid Name or ID")
                    submitted = False
 

            if submitted:
                emp = {
                    "id":id,
                    "name":name,
                    "age":age,
                    "department":department
                }
                res = requests.post(f"{API_URL}/employess", json=emp)
                if res.status_code == 201 or res.status_code == 200:
                    st.success(f"Employee added successfully!")
                else:
                    st.write(res.text)
                    st.error(f"{res}Enter Valid Detilas")   
                    
    except Exception as error:
        st.write(error)                

def update_details():
    try:
        st.subheader("Update Details")
        id = st.text_input("Enter Employee ID (10 characters, A-Z, 0-9)")

        if id:
            id_res = requests.get(f"{API_URL}/read1/{id}")
            try:
                id_data = id_res.json()
            except Exception as e:
                st.write(e)

            if len(id) == 10:
                if  id == id_data["id"]:
                    with st.form("update_employee_form"): 
                        name = st.text_input("Name", placeholder="No special char allowed")
                        age = st.number_input("Age", min_value=19, max_value=70)
                        department = st.selectbox("Department", ["AI&WEB ", "Testing", "HR", "SalesForce"])
                        submitted = st.form_submit_button("Update Employee")  

                        if name :
                            if not re.match(name_match, name):
                                st.error("Name Invalid")
                                submitted = False
                            
                        if submitted:
                            updated_employee = {
                                "name": name,
                                "age": age,
                                "department": department
                            }
                            res = requests.put(f"{API_URL}/update/{id}", json=updated_employee)

                            if res.status_code in [200, 201]:
                                st.success("Employee Updated Successfully!")
                            else:
                                st.error(f" Update failed: {res.text}")
                else:
                    st.error(f'{id} This ID not exist') 
            else:
                st.error("Invalid ID")        
    except Exception as error:
        st.write(error)


def delete_details():
    try:
        col1, col2 = st.columns([3, 1])  
        with col1:
            emp_id = st.text_input("Employee ID", max_chars=10, help="Length must be 10")
            if emp_id:
                if len(emp_id) == 10:
                    id_res = requests.get(f"{API_URL}/read1/{emp_id}")
                    id_data = id_res.json()
                    # st.write("API Response:", id_data)
                    emp_id_api = id_data.get("id")
                    if emp_id_api:
                        if emp_id == emp_id_api:
                            if emp_id and st.button("Delete"):
                                del_response = requests.delete(f"{API_URL}/delete/{emp_id}")
                                st.success(f"Employee : {emp_id} Removed")
                    else:
                        st.error(f"Employee: {emp_id} is not exist")        
                else:
                    st.error("Invalid ID") 

        with col2:
            st.markdown("<br>", unsafe_allow_html=True) 
            if st.button("Delete All"):
                res = requests.delete(f"{API_URL}/delete_all/False")  
                st.success('Data Cleared')

    except Exception as error:
        st.write(error) 



        


        


