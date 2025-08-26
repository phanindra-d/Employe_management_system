import streamlit as st
from PIL import Image
import pandas as pd
from app import view_details, add_details, update_details, delete_details


st.title(" 👨‍💼 Employee Management System")
st.subheader("Seamless Employee Data Handling")
tab1, tab2, tab3, tab4 = st.tabs(["View Employess","Add Employee","Update Employee","Clear Employee Data"])

#Viewning The details
with tab1:
    if st.button("View Details"):
        view_details()
    
#Adding new employee  
with tab2:
   add_details() 

#Updating the Data
with tab3:
    update_details()
   
#Deleting the Data            
with tab4:
    delete_details()
