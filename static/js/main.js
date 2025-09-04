// Validate employee ID format (ASP + 7 digits)
function validateEmployeeId(id) {
    const pattern = /^ASP\d{7}$/;  
    return pattern.test(id);
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded");

    // Add Employee Form Handler
    const addEmployeeForm = document.getElementById('addEmployeeForm');
    if (addEmployeeForm) {
        console.log("Found add employee form");
        
        addEmployeeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Form submitted");
            
            const id = document.getElementById('emp_id').value;
            const name = document.getElementById('emp_name').value;
            const age = document.getElementById('emp_age').value;
            const department = document.getElementById('emp_department').value;
            
            console.log("Form values:", { id, name, age, department });
            
            // Basic validation
            if (!id || !name || !age || !department) {
                alert('Please fill all fields');
                return;
            }
            
            if (!validateEmployeeId(id)) {
                alert('Invalid ID format. Must be ASP followed by 7 digits');
                return;
            }
            
            const employeeData = {
                id: id,
                name: name,
                age: parseInt(age),
                department: department
            };
            
            console.log("Sending data:", employeeData);
            
            // Send POST request to server
            fetch('/employess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(employeeData)
            })
            .then(response => {
                console.log("Response status:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("Response data:", data);
                if (data.message === 'Success') {
                    alert('Employee added successfully!');
                    addEmployeeForm.reset();
                } else {
                    alert('Failed to add employee: ' + (data.detail || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert('Error adding employee: ' + error.message);
            });
        });
    } else {
        console.error("Add employee form not found");
    }

    // Search Employee Handler - replace the current implementation with this one
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const empId = document.getElementById('search_emp_id').value;
            
            if (!validateEmployeeId(empId)) {
                alert('Invalid ID format. Must be ASP followed by 7 digits');
                return;
            }
            
            console.log('Searching for employee with ID:', empId);
            
            // Clear previous form data
            document.getElementById('update_name').value = '';
            document.getElementById('update_age').value = '';
            document.getElementById('update_department').value = '';
            document.getElementById('updateBtn').disabled = true;
            
            fetch(`/read1/${empId}`)
                .then(response => {
                    console.log('Search response status:', response.status);
                    
                    // Check if the response is JSON before trying to parse it
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        return response.json().then(data => {
                            if (!response.ok) {
                                throw new Error(data.detail || 'Server error');
                            }
                            return data;
                        });
                    } else {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.text().then(text => {
                            try {
                                return JSON.parse(text);
                            } catch (e) {
                                throw new Error('Invalid JSON response from server');
                            }
                        });
                    }
                })
                .then(data => {
                    console.log('Search response data:', data);
                    
                    if (data && data.Result && data.Result.length > 0) {
                        const employee = data.Result[0];
                        document.getElementById('update_name').value = employee.name;
                        document.getElementById('update_age').value = employee.age;
                        document.getElementById('update_department').value = employee.department;
                        document.getElementById('updateBtn').disabled = false;
                    } else {
                        alert('Employee not found');
                    }
                })
                .catch(error => {
                    // Log the full error to console for debugging
                    console.error('Search error:', error);
                    
                    // Display a user-friendly message
                    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                        alert('Network error. Please check your connection.');
                    } else if (error.message) {
                        alert('Error searching employee: ' + error.message);
                    } else {
                        alert('Unknown error occurred while searching for employee');
                    }
                });
        });
    }

    // Update Employee Form Handler - fixed version
    const updateEmployeeForm = document.getElementById('updateEmployeeForm');
    if (updateEmployeeForm) {
        updateEmployeeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const empId = document.getElementById('search_emp_id').value;
            const name = document.getElementById('update_name').value;
            const age = document.getElementById('update_age').value;
            const department = document.getElementById('update_department').value;
            
            if (!validateEmployeeId(empId)) {
                alert('Invalid ID format. Must be ASP followed by 7 digits');
                return;
            }
            
            const employeeData = {
                name: name,
                age: parseInt(age),
                department: department
            };
            
            console.log('Updating employee:', empId, 'with data:', employeeData);
            
            // Get token from cookies since you're storing it there in the login endpoint
            function getCookie(name) {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }
            
            const token = getCookie('access_token');
            
            fetch(`/update/${empId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(employeeData),
                credentials: 'include' // Include cookies in request
            })
            .then(response => {
                console.log('Update response status:', response.status);
                
                if (!response.ok) {
                    return response.json().then(errData => {
                        console.error('Error data:', errData);
                        throw new Error(errData.detail || 'Server error');
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Update response data:', data);
                
                if (data && (data.Result || data.message === 'Success')) {
                    alert('Employee updated successfully!');
                    document.getElementById('search_emp_id').value = '';
                    updateEmployeeForm.reset();
                    document.getElementById('updateBtn').disabled = true;
                } else {
                    alert('Failed to update employee');
                }
            })
            .catch(error => {
                console.error('Update error:', error);
                // Use error.message instead of the whole error object
                alert('Error updating employee: ' + error.message);
            });
        });
    }

    // Load all employees - fixed function
    function loadAllEmployees() {
        console.log('Loading all employees...');
        
        fetch('/read')
            .then(response => {
                console.log('Read all response status:', response.status);
                
                if (!response.ok) {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        return response.json().then(errData => {
                            console.error('Error data:', errData);
                            throw new Error(errData.detail || 'Failed to fetch employees');
                        });
                    } else {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                }
                return response.json();
            })
            .then(data => {
                console.log('Read all response data:', data);
                
                const employeeList = document.getElementById('employeeList');
                employeeList.innerHTML = '';
                
                if (data && data.Result && data.Result.length > 0) {
                    data.Result.forEach(employee => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${employee.id}</td>
                            <td>${employee.name}</td>
                            <td>${employee.age}</td>
                            <td>${employee.department}</td>
                            <td class="action-buttons">
                                <button class="btn btn-danger btn-delete" data-id="${employee.id}">Delete</button>
                            </td>
                        `;
                        employeeList.appendChild(row);
                    });
                    
                    // Add event listeners for delete buttons
                    document.querySelectorAll('.btn-delete').forEach(button => {
                        button.addEventListener('click', function() {
                            const empId = this.getAttribute('data-id');
                            if (confirm(`Are you sure you want to delete employee ${empId}?`)) {
                                deleteEmployee(empId);
                            }
                        });
                    });
                } else {
                    const row = document.createElement('tr');
                    row.innerHTML = '<td colspan="5" class="text-center">No employees found</td>';
                    employeeList.appendChild(row);
                }
            })
            .catch(error => {
                console.error('View error:', error);
                alert('Error loading employees: ' + error.message);
            });
    }

    // View All Employees Button Handler
    const viewEmployeesBtn = document.getElementById('viewEmployeesBtn');
    if (viewEmployeesBtn) {
        viewEmployeesBtn.addEventListener('click', function() {
            const listSection = document.getElementById('employeeListSection');
            if (listSection.style.display === 'none' || listSection.style.display === '') {
                listSection.style.display = 'block';
                loadAllEmployees();
            } else {
                listSection.style.display = 'none';
            }
        });
    }

    // Delete employee function - updated version
    function deleteEmployee(empId) {
        console.log(`Attempting to delete employee with ID: ${empId}`);
        
        // No need for authorization token for now (assuming you've removed token dependency in your backend)
        fetch(`/delete/${empId}`, {
            method: 'DELETE'
        })
        .then(response => {
            console.log('Delete response status:', response.status);
            
            if (!response.ok) {
                // Handle error response
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return response.json().then(errData => {
                        console.error('Error data:', errData);
                        throw new Error(errData.detail || 'Failed to delete employee');
                    });
                } else {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
            }
            return response.json();
        })
        .then(data => {
            console.log('Delete response data:', data);
            
            if (data && (data.message === 'Success' || data.Result)) {
                alert('Employee deleted successfully!');
                loadAllEmployees(); // Refresh the list
            } else {
                alert('Failed to delete employee: ' + (data.detail || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Delete error:', error);
            alert('Error deleting employee: ' + error.message);
        });
    }
});